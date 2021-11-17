from os import environ as env
from chromedriver_py import binary_path
import traceback
import schedule
from time import sleep
from selenium.webdriver import Chrome
from threading import Thread
from typing import NoReturn, Tuple

from telegram import(
    Update,
    Bot,
    ParseMode
)

from telegram.ext import(
    Updater,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)

_browser: Chrome = Chrome(executable_path = binary_path)
_flag: bool = True
_elementId: str = ''
_secondNumber: int = 0
_END: int = ConversationHandler.END
_TIMEOUT: int = ConversationHandler.TIMEOUT
_SHORTENED_LINK: int = 0
_ELEMENT_ID: int = 1
_HOW_MANY: int = 2
_ENABLE_JOB: int = 3
_DISABLE_JOB: int = 4
_DELETE_JOB: int = 5
_jobs_list: list = []
_bot: Bot = None
_chat_id: Tuple[str, int] = None
_message: str = ''
_messages_list: list = []

class _MyJob:
    def __init__(self, browser: Chrome, elementId: str):
        self._id: str = ''
        self._buttonElement = browser.find_element_by_id(elementId)
        self._started: bool = False
        self._deleted: bool = False
        self._state: bool = True
        self._counter: int = 0
        self._job: schedule.Job = schedule.every().second        
    
    def _job_func(self) -> NoReturn:
        global _messages_list, _bot
        if self._state:                     
            self._buttonElement.click()
            self._counter += 1            
            if len(_messages_list) != 0:
                for msg in _messages_list:
                    if self._id in msg.text:
                        try:
                            _bot.edit_message_text(
                                chat_id = msg.chat_id,
                                message_id = msg.message_id,
                                text = '<b>'
                                       f'{self._id} \n\n'
                                       f'Number of clicks: {self._counter}'
                                       '</b>',
                                parse_mode = ParseMode.HTML
                            )
                        except:
                            pass
                        break
               
    def start(self) -> NoReturn:
        self._started = True
        self._job.do(self._job_func)  
              
    def set_id(self, job_id: bool) -> NoReturn:
        self._id = job_id 
    
    def set_state(self, state: bool) -> NoReturn:
        self._state = state
    
    def set_deleted(self, deleted: bool) -> NoReturn:
        self._deleted = deleted
    
    was_started = lambda self: self._started
    was_deleted = lambda self: self._deleted
    get_counter = lambda self: self._counter
    get_id = lambda self: self._id
    get_job = lambda self: self._job
    
def _helpBot(ud: Update, ctx: CallbackContext) -> NoReturn:
    global _flag, _bot, _chat_id, _messages_list
    if _bot == _chat_id == None:
        _bot = ctx.bot
        _chat_id = ud.message.chat_id
    if len(_messages_list) != 0:
        for msg in _messages_list:
            _bot.delete_message(
                chat_id = msg.chat_id,
                message_id = msg.message_id
            )
        _messages_list.clear()
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>'
               '<u>\n Helpy Message:</u> \n\n\n'
               '/start - Initializes bot. \n\n'
               '/help - Show this message. \n\n'
               '/addjob - Add one shortened link. \n\n'
               '/enablejob - If it`s disable, enable job. \n\n'
               '/disablejob - If it`s enable(it is by default after add it), disable job. \n\n'
               '/deletejob - Delete a job. \n\n'
               '/deletealljobs - Empty jobs`s list. \n\n'
               '/showjobs - Show all jobs aviable.'
               '</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False

def _start(ud: Update, ctx: CallbackContext) -> NoReturn:
    global _flag, _bot, _chat_id, _messages_list
    if _bot == _chat_id == None:
        _bot = ctx.bot
        _chat_id = ud.message.chat_id
    if len(_messages_list) != 0:
        for msg in _messages_list:
            _bot.delete_message(
                chat_id = msg.chat_id,
                message_id = msg.message_id
            )
        _messages_list.clear()
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>Hello. Wellcome!</b>',
        parse_mode = ParseMode.HTML
    )
    _helpBot(ud, ctx)
        
def _initConversation(ud: Update, ctx: CallbackContext) -> int:
    global _flag, _END, _SHORTENED_LINK, _ENABLE_JOB, _DISABLE_JOB, _DELETE_JOB, _bot, _chat_id, _jobs_list, _messages_list
    if _bot == _chat_id == None:
        _bot = ctx.bot
        _chat_id = ud.message.chat_id
    if len(_messages_list) != 0:
        for msg in _messages_list:
            _bot.delete_message(
                chat_id = msg.chat_id,
                message_id = msg.message_id
            )
        _messages_list.clear()
    if ud.message.text == '/addjob':
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Type shortened link.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
        return _SHORTENED_LINK
    elif len(_jobs_list) == 0:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Sorry, you can`t use that command if you don`t has entered any job.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
        return _END
    elif ud.message.text == '/enablejob':        
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Type Job number to enable.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
        return _ENABLE_JOB
    elif ud.message.text == '/disablejob':
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Type Job number to disable.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
        return _DISABLE_JOB
    elif ud.message.text == '/deletejob':
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Type Job number to delete.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
        return _DELETE_JOB
    
def _catchShortenedLink(ud: Update, ctx: CallbackContext) -> int:
    global _flag, _browser, _ELEMENT_ID, _END   
    _shortenedLink: str = ''
    _shortenedLink = ud.message.text    
    if not _shortenedLink.startswith('https://oke.io'):      
        ud.message.reply_html(           
            text = '<b>'
                   'Invalid shortened link. It must be like this: \n\n'
                   'https://oke.io/<.....>'
                   '</b>' 
        )
        return _END
    _browser.get(_shortenedLink)    
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>Type element id.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    return _ELEMENT_ID
    
def _elementIdCatcher(ud: Update, ctx: CallbackContext) -> int:
    global _flag, _elementId, _HOW_MANY    
    _elementId = ud.message.text    
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>Type how many times do you want repeat this job.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    return _HOW_MANY
    
def _repeatUntill(ud: Update, ctx: CallbackContext) -> int:
    global _browser, _elementId, _END, _jobs_list
    _rn: int = 0
    _msg: str = ud.message.text
    if _msg.isdigit():
        _rn = int(_msg)
        index: int = 0
        while index < _rn:
            _jobs_list.append(_MyJob(_browser, _elementId))
            index += 1
    else:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Repetitions`s number must be an integer number.</b>',
            parse_mode = ParseMode.HTML
        )
        return _END        
    return _END
    
def _enableJob(ud: Update, ctx: CallbackContext) -> int:
    global _flag, _jobs_list, _END
    number: int = 0
    if ud.message.text.isdigit():                   
        number = int(ud.message.text)
        if number < 0 or number > len(_jobs_list):
            ctx.bot.send_message(
                chat_id = ud.message.chat_id,
                text = '<b>'
                       'Invalid Job number. \n\n'
                       f'Jub number must be lower than number of jobs: {len(_jobs_list)} '
                       'and bigger than 0.'
                       '</b>',
                parse_mode = ParseMode.HTML
            ) 
            return _END
    else:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Job number must be an integer number.</b>',
            parse_mode = ParseMode.HTML
        )
        return _END
    _jobs_list[number-1].set_state(True)
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = f'<b>Job {number} was enable.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    return _END
    
def _disableJob(ud: Update, ctx: CallbackContext) -> int:
    global _flag, _jobs_list, _END
    number: int = 0
    if ud.message.text.isdigit():                   
        number = int(ud.message.text)
        if number < 0 or number > len(_jobs_list):
            ctx.bot.send_message(
                chat_id = ud.message.chat_id,
                text = '<b>'
                       'Invalid Job number. \n\n'
                       f'Jub number must be lower than number of jobs: {len(_jobs_list)} '
                       'and bigger than 0.'
                       '</b>',
                parse_mode = ParseMode.HTML
            ) 
            return _END
    else:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Job number must be an integer number.</b>',
            parse_mode = ParseMode.HTML
        )
        return _END
    number = int(ud.message.text)
    _jobs_list[number-1].set_state(False)
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = f'<b>Job {number} was disable.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    return _END
    
def _deleteJob(ud: Update, ctx: CallbackContext) -> int:
    global _jobs_list, _END
    number: int = 0
    if ud.message.text.isdigit():                   
        number = int(ud.message.text)
        if number <= 0 or number > len(_jobs_list):
            raise ValueError(
                'Invalid Job number. \n\n'
                f'Jub number must be lower than number of jobs: {len(_jobs_list)} '
                'and bigger than 0.'
        ) 
    else:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>Job number must be an integer number.</b>',
            parse_mode = ParseMode.HTML
        )
        return _END
    number = int(ud.message.text)
    _jobs_list[number-1].set_deleted(True)
    return _END
    
def _deleteAllJobs(ud: Update, ctx: CallbackContext) -> NoReturn:
    global _flag, _jobs_list, _messages_list, _bot, _chat_id
    if _bot == _chat_id == None:
        _bot = ctx.bot
        _chat_id = ud.message.chat_id
    if len(_messages_list) != 0:
        for msg in _messages_list:
            _bot.delete_message(
                chat_id = msg.chat_id,
                message_id = msg.message_id
            )
        _messages_list.clear()
    for job in _jobs_list:
        schedule.cancel_job(job.get_job())
    _jobs_list.clear()
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>The jobs`s list was emptied.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    
def _showJobs(ud: Update, ctx: CallbackContext) -> NoReturn:
    global _flag, _jobs_list, _messages_list, _bot, _chat_id
    if _bot == _chat_id == None:
        _bot = ctx.bot
        _chat_id = ud.message.chat_id
    if len(_messages_list) != 0:
        for msg in _messages_list:
            _bot.delete_message(
                chat_id = msg.chat_id,
                message_id = msg.message_id
            )
        _messages_list.clear()
    if len(_jobs_list) == 0:
        ctx.bot.send_message(
            chat_id = ud.message.chat_id,
            text = '<b>There are no jobs aviable.</b>',
            parse_mode = ParseMode.HTML
        )
        _flag = False
    else:
        index: int = 0
        while index < len(_jobs_list):
            _messages_list.append(ctx.bot.send_message(
                chat_id = ud.message.chat_id,
                text = '<b>'
                       f'{_jobs_list[index].get_id()} \n\n'
                       f'Number of clicks: {_jobs_list[index].get_counter()}'
                       '</b>',
                parse_mode = ParseMode.HTML
            ))
            index += 1
        _flag = False
        
def _timeout(ud: Update, ctx: CallbackContext ) -> int:
    global _flag, _END
    ctx.bot.send_message(
        chat_id = ud.message.chat_id,
        text = '<b>The timeout for conversation was exceeded. Please restart it.</b>',
        parse_mode = ParseMode.HTML
    )
    _flag = False
    return _END 
    
def _errorHandler(ud: Update, ctx: CallbackContext) -> NoReturn:
    global _flag, _bot, _chat_id
    tb_list = traceback.format_exception(None, ctx.error, ctx.error.__traceback__)
    tb_string = ''.join(tb_list)
    print(tb_string)
    _bot.send_message(
        chat_id = _chat_id,        
        text = f'<b>{ctx.error}</b>',
        parse_mode = ParseMode.HTML
    )
    
def _job_func() -> NoReturn:
    global _flag, _secondNumber, _message, _bot, _chat_id, _jobs_list
    if _bot == _chat_id == None:       
        return
    index: int = 0
    while index < len(_jobs_list):
        if _jobs_list[index].was_deleted():
            schedule.cancel_job(_jobs_list[index].get_job())
            del _jobs_list[index]
            _bot.send_message(
                chat_id = _chat_id,
                text = f'<b>Job {index + 1} was deleted.</b>',
                parse_mode = ParseMode.HTML
            )
            _flag = False
        elif not _jobs_list[index].was_started():
            _jobs_list[index].start()            
            _bot.send_message(
                chat_id = _chat_id,
                text = f'<b>Job {index + 1} was started.</b>',
                parse_mode = ParseMode.HTML
            )
            _flag = False 
        elif _jobs_list[index].was_started() and not _jobs_list[index].was_deleted():     
            _jobs_list[index].set_id(job_id = f'Job {index + 1}')           
            index += 1                     
    _secondNumber += 1
    if not _flag:
        _secondNumber = 0
        _flag = True
    if _secondNumber == 1740:
        _secondNumber = 0
        if _message != None:
            _bot.delete_message(
                chat_id = _message.chat_id,
                message_id = _message.message_id 
            )
        _message = _bot.send_message(
            chat_id = _chat_id,
            text = '<b>The bot is working...!!!</b>',
            parse_mode = ParseMode.HTML
        )

def _schedulerFunc() -> NoReturn: 
    schedule.every().second.do(_job_func)
    while True:
        schedule.run_pending()
        sleep(1)
    
def _main():
    updater = Updater(token = env['TOKEN'])
    dispatcher = updater.dispatcher
    
    dispatcher.add_error_handler(_errorHandler)
    
    dispatcher.add_handler(CommandHandler('start',_start))
    dispatcher.add_handler(CommandHandler('help',_helpBot))
    dispatcher.add_handler(ConversationHandler(
       entry_points = [
           CommandHandler(['addjob','enablejob','disablejob','deletejob'],_initConversation)
       ],
       states = {
           _SHORTENED_LINK: [MessageHandler(Filters.text, _catchShortenedLink)],
           _ELEMENT_ID: [MessageHandler(Filters.text, _elementIdCatcher)],
           _HOW_MANY: [MessageHandler(Filters.text, _repeatUntill)],
           _ENABLE_JOB: [MessageHandler(Filters.text, _enableJob)],
           _DISABLE_JOB: [MessageHandler(Filters.text, _disableJob)],
           _DELETE_JOB: [MessageHandler(Filters.text, _deleteJob)],
           _TIMEOUT: [MessageHandler(Filters.text, _timeout)]
       },
       fallbacks = [],
       conversation_timeout = 180
    ))
    dispatcher.add_handler(CommandHandler('deletealljobs', _deleteAllJobs))
    dispatcher.add_handler(CommandHandler('showjobs', _showJobs))
    
    updater.start_polling(allowed_updates = Update.ALL_TYPES)
    updater.idle()         

if __name__ == '__main__':
    thr1: Thread = Thread(target = _main)
    thr2: Thread = Thread(target = _schedulerFunc)
    thr1.start()
    thr2.start()






