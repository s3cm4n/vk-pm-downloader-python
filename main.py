import utils as u
import vk_api as v
WAIT_TIME = u.WAIT_TIME

# Load myself and create dir
u.info("Загрузка текущего профиля")
me = v.get_user()
u.info("Текущий профиль:",v.gen_name(me))

done = u.done_read(me)
if done['uid'] == me['uid']:
    u.warning("Найден файл сохранения для этого профиля.\nЕсли вам надо начать заново, просто удалите файл %s." % done['filename'])
    dirname = v.gen_dir_name(me) #v.gen_name(me) + '_' + str(me['uid'])
else:
    u.info("Создание директории")
    dirname = v.gen_dir_name(me) 
    dirname = u.mklsdir(dirname)
    u.info("Текущая директория:", dirname)
    done['uid'] = me['uid']

u.info("Загрузка диалогов")
dialogs = v.get_dialogs()

u.info("Всего %d диалогов" % len(dialogs))
"Загрузка личных сообщений:"
for idx,dialog in enumerate(dialogs):
    u.sleep(WAIT_TIME)
    
    file = None

    if dialog['uid'] <= 0:      # Is group message
        u.warning("Сообщения с группой (id={}) не поддерживаются".format(dialog['uid']))
    elif 'chat_id' in dialog:   # Is chat message
        u.info("Беседа '%s'" % dialog['title'])
        if dialog['chat_id'] in done['chat']:
            u.info('Уже загружено')
            continue
        messages = v.get_group_messages(dialog['chat_id'])
        u.info("Всего %d сообщений"%len(messages))
        file = u.getlsfile(dirname,dialog['title'].replace(' ','_') + '_' + str(dialog['chat_id'])+'.html')
        u.writeheader(file)

        
        u.print_pb(0)
        for i,message in enumerate(messages):
            u.print_pb(i/len(messages))
            user = v.get_user(message['uid'])
            file.write(v.gen_div_by_message(message,user).encode("UTF-8"))
        u.print_pb(1)
        print()
        u.writefooter(file)
        file.close()
        done['chat'].append(dialog['chat_id'])
    else:                       # Is private message
        user = v.get_user(dialog['uid'])
        u.info("Личные сообщения с %s" % v.gen_name(user))
        if dialog['uid'] in done['private']:
            u.info('Уже загружено')
            continue
        messages = v.get_private_messages(user['uid'])
        u.info("Всего {} сообщений".format(len(messages)))
        file = u.getlsfile(dirname,v.gen_name(user) + '_' + str(user['uid'])+'.html')
        u.writeheader(file)
        u.print_pb(0)
        for i,message in enumerate(messages):
            u.print_pb(i/len(messages))
            sender = None
            if message['out'] == 1:
                sender = me
            else:
                sender = user
            file.write(v.gen_div_by_message(message,sender).encode("UTF-8"))
        u.print_pb(1)
        print()
        u.writefooter(file)
        file.close()
        done['private'].append(dialog['uid'])
    u.info("Загружено диалогов %d из %d (%d%%)" % (idx+1,len(dialogs),int(((idx+1)/len(dialogs))*100)))
    u.done_write(done)
u.done_remove(done)