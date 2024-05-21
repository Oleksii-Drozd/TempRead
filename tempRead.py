import datetime
import serial
import serial.tools.list_ports as port_list
from threading import Thread
import decimal
from datetime import datetime
import mysql.connector
from mysql.connector import Error

global temper, temperDate


def connectDB():
    try:
        connection = mysql.connector.connect(host='host',
                                             port='3306',
                                             database='nameDB',
                                             user='root',
                                             password='password')
        return connection
    except Error as e:
        print("Error connecting to MySQL database:", str(e))
        raise


def resultSaveToBase():
    connection = None
    cursor = None
    try:
        connection = connectDB()

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute('select tempValue from smartHome.Temperature order by tempDate desc limit 2')
            rows = cursor.fetchall()

            if rows[0][0] != temper and rows[1][0] != temper:
                mySql_insert_query = "INSERT INTO Temperature (tempDate, tempValue) values (now(), %s)"
                cursor = connection.cursor()
                cursor.execute(mySql_insert_query, (temper,))
                connection.commit()

    except Exception as e:
        print("Error:", str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def temperatureMeasurementThread():
    ports = list(port_list.comports())
    port = ports[0].device

    global temper
    global temperDate

    while True:
        try:
            serialPort = serial.Serial(port)
            serialString = serialPort.readline().decode("utf-8")
            serialPort.close()

            temperDate = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            temper = decimal.Decimal(serialString)

            resultSaveToBase()

        except Exception as e:
            print("Error:", str(e))


if __name__ == "__main__":
    print("version 2.0.1")
    while True:
        temperatureMeasurementThread()
