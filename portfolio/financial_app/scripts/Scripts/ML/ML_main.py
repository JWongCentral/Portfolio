
#commands:
#conda activate tf

import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Input, concatenate
from sklearn.metrics import mean_squared_error, mean_absolute_error,r2_score


#To use GPU
#os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
#os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use the correct GPU device index
#physical_devices = tf.config.list_physical_devices('GPU')
#tf.config.experimental.set_memory_growth(physical_devices[0], True)


#creating the model based off of current data
#this training data will try to predict the year 2022 data from ALL relevant data
def main():
    data = preprocessing()
    
    X_train = data['X_train']
    X_val = data['X_val']
    features_train = data['features_train']
    features_val = data['features_val']
    company_ids_train = data['company_ids_train']
    company_ids_val = data['company_ids_val']
    
    # Build the LSTM model
    input_features = Input(shape=(X_train.shape[1], X_train.shape[2]))
    input_company = Input(shape=(1,))

    x = LSTM(units=50, return_sequences=True)
    x = x(input_features)
    
    x = LSTM(units=50, return_sequences=False)(x)
    # Repeat the company ID for all time steps
    company_ids_repeated = concatenate([input_company] * X_train.shape[1])

    merged = concatenate([x, company_ids_repeated])
    output = Dense(units=X_train.shape[2])(merged)

    model = Model(inputs=[input_features, input_company], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error')

    model.summary()

    # Train the model
    model.fit([X_train, company_ids_train.reshape((-1, 1))], features_train, epochs=50, batch_size=32, validation_data=([X_val, company_ids_val.reshape((-1, 1))], features_val))

    # Evaluate the model
    y_pred = model.predict([X_val, company_ids_val.reshape((-1, 1))])
    mse = mean_squared_error(features_val, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(features_val, y_pred)
    r2 = r2_score(features_val, y_pred)

    print(f"Mean Squared Error: {mse:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
    print(f"Mean Absolute Error: {mae:.4f}")
    print(f"R-squared: {r2:.4f}")

#return data as a list of all possible tickers and in a dictionary
def preprocessing(src = './SEC_files/Ticker'):
    ret = pd.DataFrame()
    counter = 0
    for file in os.listdir(src):
        data = pd.read_csv(src+'/'+file,index_col=0)
        ticker = file.replace('.csv','')
        data = data.T
        data['ticker']=ticker
        
        if counter >= 2:
            break
        else:
            ret = pd.concat([ret,data],axis=0,)
            counter+=1

    sc = MinMaxScaler(feature_range=(0,1))
    scaled_data = sc.fit_transform(ret[['cash_and_equiv', 'net_income', 'eps_diluted', 'long_term_debt', 'long_term_assets', 'depreication', 'revenue']])
    X_features = scaled_data[:-1]
    company_ids = ret['ticker'].values[:-1]
    label_encoder = LabelEncoder()
    encoded_company_ids = label_encoder.fit_transform(company_ids)
    X_train, X_val, features_train, features_val, company_ids_train, company_ids_val = train_test_split(
        X_features, X_features, encoded_company_ids , test_size=0.2, shuffle=False
    )   
    #reshaping to 3d for lstm model
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_val = X_val.reshape((X_val.shape[0], X_val.shape[1], 1))

    print(data.info())
    return {
        'X_train':X_train,
        'X_val':X_val,
        'features_train':features_train,
        'features_val':features_val,
        'company_ids_train':company_ids_train,
        'company_ids_val':company_ids_val,
    }
    
        
def test_computer():
    # Check if GPU is available
    if tf.config.experimental.list_physical_devices('GPU'):
        print("GPU is available")
        print(tf.config.experimental.list_physical_devices('GPU'))
    else:
        print("GPU is NOT available")

    # Test GPU with a simple computation
    a = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0])
    b = tf.constant([5.0, 4.0, 3.0, 2.0, 1.0])
    c = a + b

    print("Result of GPU computation:")
    print(c)

if __name__ == '__main__':
    main()