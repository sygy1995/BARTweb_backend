# for sending e-mail to user
import os, sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml

from utils import model_logger as logger

def get_config(user_path):
    '''
    load data from user.config

    '''
    config_file = os.path.join(user_path, 'user.config')

    # handle non-existing exception
    if not os.path.exists(config_file):
        return None

    with open(config_file, 'r') as fopen:
        user_data = yaml.load(fopen)

    return user_data

def send_email(user_email,title,message):
    HOST_ADDRESS = "zanglab.service@gmail.com"
    PASSWORD = "ZangLab2018"
    msg = MIMEMultipart()
    msg['From'] = HOST_ADDRESS
    msg['To'] = user_email
    msg['Subject'] = title
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP_SSL("smtp.gmail.com")
    try:
        server.login(HOST_ADDRESS, PASSWORD)
        msg = msg.as_string()
        server.sendmail(HOST_ADDRESS, user_email, msg)
    except smtplib.SMTPAuthenticationError:
        return False, "username or password is wrong"
    except:
        return False, "errors in sending key to e-mail..."
    finally:
        server.quit()  # finally close the connection with server
    
    return True, "send e-mail to user successfully..."

def send_email_message(user_data):
    user_key = user_data['user_key']
    email = user_data['user_email']
    dataType = user_data['dataType']
    
    message_body = ''
    return_flag = False
    return_message = ''
    if email != '':
        # BART successfully done
        if if_success(path,dataType):
            message_body = '''
Congratulations! Your BART job is done!

Please get the results through this link: {}
'''.format('http://bartweb.org/result?user_key='+user_key)
            title = 'BART result'
            return_flag,return_message = send_email(email,title,message_body)

        # BART ends with error
        else:
            message_body = '''
Unfortunately, your BART job ends with errors.

Please check whether you chose the correct species or uploaded the required format file.

Or reach us at wm9tr@virginia.edu with your key: {}

'''.format(user_key)
            title = 'BART error'
            return_flag,return_message = send_email(email,title,message_body)
    
    if return_flag:
        logger.info("Send e-mail: {}".format(return_message))
    else:
        logger.error("Send e-mail: {}".format(return_message))

# if file is zero
def is_zero(file):
    return True if os.path.getsize(file) == 0 else False

def if_success(user_path,dataType):
    done = False
    bart_output_dir = user_path+'/download/'
    files = os.listdir(bart_output_dir)
    count = 0

    # for genelist input
    if dataType == 'Geneset':
        for file in files:
            if is_zero(os.path.join(bart_output_dir, file)):
                continue

            if '_auc.txt' in file:
                count = count+1
            if '_bart_results.txt' in file:
                count = count+1
            if '_adaptive_lasso_Info.txt' in file: 
                count = count+1
            if '_enhancer_prediction_lasso.txt' in file: 
                count = count+1
        if count == 4:
            done = True

    # for ChIP-seq input
    if dataType == 'ChIP-seq':
        for file in files:
            if is_zero(os.path.join(bart_output_dir, file)):
                continue
    
            if '_auc.txt' in file: 
                count = count+1
            if '_bart_results.txt' in file: 
                count = count+1
        if count == 2:
            done = True
    return done

if __name__ == '__main__':
    path = sys.argv[1]
    user_data = get_config(path)
    send_email_message(user_data)