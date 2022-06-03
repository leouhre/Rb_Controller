#!Manually change RB-controller parameters here. RUN TO SAVE
import shelve

def write_config():
    with shelve.open('config') as config:
        config['kp'] = 13.45
        config['ki'] = 0.4315
        config['kd'] = 98
        config['temperature_limit'] = 210.0
        config['temperature_offset'] = 0.0
        config['max_fluctuations'] = 1
        config['settle_slope'] = 0.1
        config['slope_length'] = 101
        config['settle_wait_time'] = 2.0
        config['alpha'] = 0.1
        config['freq'] = 2.0

if __name__ == '__main__':
    write_config()

