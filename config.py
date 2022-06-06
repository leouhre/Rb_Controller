#!Manually change RB-controller parameters here. RUN TO SAVE
import shelve

def write_config():
    with shelve.open('config') as config:
        config['kp'] = 0.9
        config['ki'] = 0.01
        config['kd'] = 0
        config['temperature_limit'] = 210.0
        config['temperature_offset'] = 0.0
        config['max_fluctuations'] = 1
        config['settle_slope'] = 0.1
        config['slope_length'] = 101
        config['settle_wait_time'] = 2.0

        #onlty changeable from config.py
        config['alpha'] = 0.8
        config['freq'] = 2.0
        config['kp2'] = 2
        config['ki2'] = 0.1
        config['kd2'] = 0

if __name__ == '__main__':
    write_config()

