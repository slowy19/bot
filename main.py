import configparser
import telebot
import random

config = configparser.ConfigParser()
config.read('config.conf')

TOKEN = config['General']['token']
DEBUG_MODE = config.getboolean('General', 'debug_mode')
bot = telebot.TeleBot(TOKEN)

players = []
table = []
table_index = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Enter players separated by a space')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global players, table, table_index
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, 'Unknown command, enter players separated by a space')
    else:
        players, table = create_teams(message)
        table_index = 0 
        next_command(message)

def create_table(N):
    table = []
    
    for i in range(2**N):
        if bin(i).count('1') == N // 2:
            c = list(bin(i)[2:].zfill(N))
            table.append(c)
    
    random.shuffle(table)
    return table

def create_teams(message):
    players = message.text.split()
    table = create_table(len(players))
    return players, table

def next_command(message):
    global players, table, table_index

    if table_index < len(table):
        row = table[table_index]
        team1 = [players[i] for i in range(len(players)) if row[i] == '1']
        team2 = [players[i] for i in range(len(players)) if row[i] == '0']
        
        team1_str = ' '.join(team1) if team1 else "No players"
        team2_str = ' '.join(team2) if team2 else "No players"
    
        command_text = f"{team1_str} \n VS \n{team2_str}"
        inline_kb = telebot.types.InlineKeyboardMarkup()
        next_button = telebot.types.InlineKeyboardButton(text="Next", callback_data='next')
        inline_kb.add(next_button)
        bot.send_message(message.chat.id, command_text, reply_markup=inline_kb)
        
        table_index += 1
    else:
        bot.send_message(message.chat.id, "That's all")

@bot.callback_query_handler(func=lambda call: call.data == 'next')
def process_callback(call):
    next_command(call.message)

def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
