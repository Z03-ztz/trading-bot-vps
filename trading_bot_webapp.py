from flask import Flask, render_template, jsonify, request
from threading import Thread
import time
import json
import pandas as pd
import datetime

app = Flask(__name__)

bot_running = False
emergency_stop = False
bot_thread = None

with open('version.txt') as vf:
    bot_version = vf.read().strip()

bot_status = {
    'capital': 1000,
    'open_trades': 0,
    'daily_profit': 0,
    'daily_loss': 0,
    'session_status': 'Inactive',
    'emergency_stop': False,
    'version': bot_version,
    'upgrade_available': False
}

with open('config.json') as f:
    config = json.load(f)

def log_trade(trade):
    df = pd.DataFrame([trade])
    df.to_csv('trade_log.csv', mode='a', header=False, index=False)

def trading_bot():
    global bot_running, emergency_stop, bot_status
    while bot_running and not emergency_stop:
        bot_status['capital'] += 5
        bot_status['daily_profit'] += 5
        bot_status['open_trades'] = 1
        bot_status['session_status'] = 'Active'

        trade = {
            'Symbol': 'EURUSD',
            'Entry Time': datetime.datetime.now(),
            'Entry Price': bot_status['capital'] - 5,
            'Stop Loss': bot_status['capital'] - 10,
            'Take Profit': bot_status['capital'] + 10,
            'Size': 1,
            'Exit Price': bot_status['capital'],
            'Exit Time': datetime.datetime.now(),
            'Profit': 5
        }
        log_trade(trade)
        time.sleep(5)

    bot_status['session_status'] = 'Stopped'
    bot_status['open_trades'] = 0

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/status')
def status():
    return jsonify(bot_status)

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_running, bot_thread
    if not bot_running:
        bot_running = True
        bot_thread = Thread(target=trading_bot)
        bot_thread.start()
    return jsonify({'message': 'Bot Started'})

@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot_running
    bot_running = False
    return jsonify({'message': 'Bot Stopped'})

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop_bot():
    global emergency_stop, bot_running
    emergency_stop = True
    bot_running = False
    bot_status['emergency_stop'] = True
    return jsonify({'message': 'Emergency Stop Activated'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
