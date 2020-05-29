'''
This is an updated version using coingecko.com API via a simple PHP page hosted at URL https://m5stack.it/btc

PHP code:
<?php
        $url = "https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false";
        $json = file_get_contents($url);
        $json = json_decode($json);
        $high_24h = $json->market_data->high_24h->usd;
        $low_24h = $json->market_data->low_24h->usd;
        $current_price = $json->market_data->current_price->usd;
        $last_updated = $json->last_updated;
        echo "{\"last_updated\":\"$last_updated\",\"high_24h\":\"$high_24h\",\"low_24h\":\"$low_24h\",\"current_price\":\"$current_price\"}";
?>
'''

from m5stack import *
from utils import *
import utime as time
import machine
import urequests
import ujson
import curl
import utils
import m5cloud
import gc


def timeout_reset(timer):
    import machine
    machine.reset()

# def save_price_csv(filename, timestamp, price):
#     if utils.exists(filename):
#         with open(filename, 'a') as f:
#             f.write(timestamp+','+price+'\n')
#     else:
#         with open(filename, 'w') as f:
#             f.write(timestamp+','+price+'\n')

t1 = machine.Timer(2)
t1.init(period=60*1000*60*6, mode=t1.PERIODIC, callback=timeout_reset)


def main():
    lcd.clear()
    lcd.setBrightness(800)
    lcd.setTextColor(lcd.WHITE, lcd.BLACK)
    lcd.font('SFArch_48.fon')
    lcd.print('BTC Price', lcd.CENTER, 25, lcd.ORANGE)
    prev_price = ''
    timereset = time.ticks_ms() + (60*1000)
    while True:
        if not m5cloud.idle():
            break
        try:
            # btc_data = get_btc_price()
            gc.collect()
            lcd.triangle(300,0, 319,0, 319,19, lcd.YELLOW, lcd.YELLOW)
            r = urequests.get('https://m5stack.it/btc.php')
            lcd.triangle(300,0, 319,0, 319,19, lcd.BLUE, lcd.BLUE)
            btc_data = ujson.loads(r.text)
            print(btc_data)
            print('')
            if btc_data:
                # Max price
                high = btc_data['high_24h']
                high = high[:(high.find('.')+3)]
                lcd.font(lcd.FONT_DejaVu18)
                lcd.print('Max:', 20, 192, lcd.GREEN)
                lcd.print(high, 5, 215, lcd.GREEN)

                # Min price
                low = btc_data['low_24h']
                low = low[:(low.find('.')+3)]
                lcd.font(lcd.FONT_DejaVu18)
                lcd.print('Min:', 255, 192, lcd.RED)
                lcd.print(low, lcd.RIGHT, 215, lcd.RED)

                # Last Price
                price = btc_data['current_price']
                if not price == prev_price:
                    lcd.rect(0, 100, 320, 48, lcd.BLACK, lcd.BLACK)
                    lcd.font('SFArch_48.fon')
                    lcd.print('$ '+price, lcd.CENTER, 100, color=lcd.WHITE)

                # Symbol
                _offset = 175
                if price > prev_price:
                  lcd.rect(140, _offset, 41, 26, lcd.BLACK, lcd.BLACK)
                  lcd.triangle(160,_offset, 140,_offset+25, 180,_offset+25, lcd.GREEN, lcd.GREEN)
                elif price < prev_price:
                  lcd.rect(140, _offset, 41, 26, lcd.BLACK, lcd.BLACK)
                  lcd.triangle(160,_offset+25, 140,_offset, 180,_offset, lcd.RED, lcd.RED)
                prev_price = price
                
                # update time
                tstr = 'Update: %s' % (btc_data['last_updated'])
                lcd.font(lcd.FONT_Default)
                lcd.print(tstr, 3, 3, 0x666666)
                
        except Exception as e:
            sys.print_exception(e)
            pass

        time.sleep(5)

main()
