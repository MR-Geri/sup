def worktime(cursor):
    cursor.execute(f'SELECT wtm_id, wrkr_id, tsk_id, wtm_start, wtm_finish, wtm_comment FROM worktime;')
    return (
        ("wtm_id", 'wrkr_id', 'tsk_id', 'Начало', 'Конец', 'Комментарий'),
        ("wtm_id", 'wrkr_id', 'tsk_id', 'wtm_start', 'wtm_finish', 'wtm_comment'),
        cursor.fetchall()
    )


def working_rate(cursor):
    cursor.execute(f'SELECT rte_id, rte_main, rte_weekend, rte_overwork FROM working_rate;')
    return (
        ('rte_id', 'Основная', 'Выходной день', 'Переработка'),
        ('rte_id', 'rte_main', 'rte_weekend', 'rte_overwork'),
        cursor.fetchall()
    )


def worker(cursor):
    cursor.execute(f'SELECT wrkr_id, rte_id, tem_name, wrkr_surname, wrkr_name, wrkr_middlename, wrkr_post FROM worker;')
    return (
        ('wrkr_id', 'rte_id', 'Команда', 'Фамилия', 'Имя', 'Отчетсво', 'Должность'),
        ('wrkr_id', 'rte_id', 'tem_name', 'wrkr_surname', 'wrkr_name', 'wrkr_middlename', 'wrkr_post'),
        cursor.fetchall()
    )


def wastes(cursor):
    cursor.execute(f'SELECT wts_id, tsk_id, wts_sum, wts_comment, wts_date FROM wastes;')
    return (
        ('wts_id', 'tsk_id', 'Сумма', 'Комментарий', 'Дата'),
        ('wts_id', 'tsk_id', 'wts_sum', 'wts_comment', 'wts_date'),
        cursor.fetchall()
    )


def team(cursor):
    cursor.execute(f'SELECT tem_name, wrkr_id FROM team;')
    return (
        ('Название', 'Начальник'),
        ('tem_name', 'wrkr_id'),
        cursor.fetchall()
    )


def task(cursor):
    cursor.execute(f'SELECT tsk_id, pjt_id, tsk_name, tsk_comment, tsk_status, tsk_create, tsk_finish FROM task;')
    return (
        ('tsk_id', 'pjt_id', 'Название', 'Комментарий', 'Статус', 'Начало', 'Конец'),
        ('tsk_id', 'pjt_id', 'tsk_name', 'tsk_comment', 'tsk_status', 'tsk_create', 'tsk_finish'),
        cursor.fetchall()
    )


def tag(cursor):
    cursor.execute(f'SELECT tag_name FROM tag;')
    return (
        ('Название', ),
        ('tag_name', ),
        cursor.fetchall()
    )


def contains(cursor):
    cursor.execute(f'SELECT tag_name, wtm_id FROM contains;')
    return (
        ('Тэг', 'wtm_id'),
        ('tag_name', 'wtm_id'),
        cursor.fetchall()
    )


def project(cursor):
    cursor.execute(f'SELECT pjt_id, clt_name, pjt_name, pjt_status, pjt_create, pjt_finish, pjt_planned_finish FROM project;')
    return (
        ('pjt_id', 'Клиент', 'Название', 'Статус', 'Создание', 'Конец', 'Планируемое время окончания'),
        ('pjt_id', 'clt_name', 'pjt_name', 'pjt_status', 'pjt_create', 'pjt_finish', 'pjt_planned_finish'),
        cursor.fetchall() 
    )


def client(cursor):
    cursor.execute(f'SELECT clt_name FROM client;')
    return (
        ('Название', ),
        ('clt_name', ),
        cursor.fetchall()
    )

