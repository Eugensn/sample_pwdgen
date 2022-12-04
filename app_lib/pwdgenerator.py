import re
import hashlib


class Password(object):
    """" Class contains settings and methods for password generation and generated password """

    # defautl mibols allowed to use
    ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    abc = 'abcdefghijklmnopqrstuvwxyz'
    dig = '0123456789'
    spec = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"  # no space!

    password_value = 'qwerty'
    sucsess = False
    error = 'error'
    simbolstr = ''
    simbol_len = 0

    def __init__(self, settings):
        self.settings = settings
        self.generate_simbolstr()

    # generate string with simbols potentialy used in password

    def generate_simbolstr(self):
        self.simbolstr = ''
        if self.settings['use_uppercase']:
            self.simbolstr += Password.ABC
        if self.settings['use_lowercase']:
            self.simbolstr += Password.abc
        if self.settings['use_digits']:
            self.simbolstr += Password.dig
        if self.settings['use_special']:
            self.simbolstr += Password.spec

        if self.settings['use_extra']:
            for ch in self.settings['extra']:
                if not (ch in self.simbolstr):
                    self.simbolstr += ch

        if self.settings['except'] != '':
            self.simbolstr = re.sub(
                '[' + self.settings['except'] + ']', '', self.simbolstr)

        self.simbolstr = "".join(sorted(self.simbolstr))
        self.simbol_len = len(self.simbolstr)

    def generate_password(self):
        ''' Password generation'''

        self.attempt_number = 0
        """" check simbol string """
        if self.simbol_len == 0:
            self.error = 'no simbols for password'
            self.sucsess = False
            return

        self.sucsess = False
        iterator = 0
        pwd_ok = False
        attempts = self.settings['attempts']

        # try to generate password

        hash_function = self.get_hash_custom if self.settings[
            'algorithm'] == 'custom' else self.get_hash_md5

        while not pwd_ok and iterator < attempts:

            hash = hash_function(iterator)

            pwd = self.get_pwd(hash)

            if self.check_pwd(pwd):
                pwd_ok = True
                self.password_value = pwd
                self.sucsess = True

            iterator += 1

        self.attempt_number = iterator

        if not self.sucsess:
            self.error = 'no password generated'

    """ Return number (decmal 'hash') from given phrace. Based on unicode point and given password length """

    def get_hash_custom(self, iterator=0, m=31):
        '''
        iterator (int) - счетчик попыток генераций
        m (int) - простое число, являющееся одим из аргументов при генерации "хеша"

        Функция получает хэш по заложенной "кастомной" функции из keyphrase на осное кодов unicode символов и возвращает десятеричное число.
        Исходя из длины количества символов, используемых при генерации пороля и требуемой длины пароля
        вычисляется min_table_size - число возможных комбинаций доступных символов при заданной в настройках длине пароля.

        Чтобы в дальшейшем полученная длина пароля была гарантированно не меньше заданной в настройках плюс один символ (который будет отрезан),
        к первично рассчитанному хэшу величиной не более min_table_size добавляется еще одно значение min_table_size и
        в итоге значение хэша будет между min_table_size  и 2*min_table_size

        secretnum - начальное значение хэша из настроек, которое может настраивать пользователь
        iterator - значение итератора, используется при вызове из цикла при последовательных попытках генерации пароля
        '''

        min_table_size = self.simbol_len**(self.settings['pwdlen'])
        start_hash = 64*10**18
        hash = start_hash + self.settings['secretnum'] + iterator
        for ch in self.settings['keyphrase']:
            hash = m * hash + ord(ch)

        hash = hash % min_table_size + min_table_size

        return hash

    def get_hash_md5(self, iterator=0):
        """ 
        Return number (decmal 'hash') from given phrace. Based on unicode point and given password length. Based on md5 algorithm 
        iterator (int)
        """

        min_table_size = self.simbol_len**(self.settings['pwdlen'])

        b = self.settings['keyphrase'].encode('utf-8')
        dec_value = int(hashlib.md5(b).hexdigest(), base=16) + iterator

        b = hex(dec_value).encode('utf-8')

        return int(hashlib.md5(b).hexdigest(), base=16) % min_table_size + min_table_size

    '''
    
    '''

    def get_pwd(self, number):
        """ 
            Make password string from given hashnumber. Based on simbol string length 
            number (imt) - hashnumber

            Формирует из переданного числового хеша пароль путем перевода числа из десятичной ситемы в
            систему счисления по основанию, равному количеству применяемых при генерации символов
        """
        ground = self.simbol_len
        goahead = True
        indx_list = []

        def get_index(number, ground):
            '''возвращает номер символа в новой системе счисления и остаток от деления'''
            indx = number % ground
            num = number // ground
            return indx, num

        # Перевод в систему счисления по базе с формированием списка символов в обраном порядке
        while goahead:
            indx, number = get_index(number, ground)
            indx_list.append(indx)
            if number < ground:
                indx_list.append(number)
                goahead = False

        # формирование строки пароля с изменением списка символов, за исключением первого (т.к. количество символов на 1 больше необходимого)
        pwd = ""

        for i in range(self.settings['pwdlen'], 0, -1):
            pwd += self.simbolstr[indx_list[i-1]]

        return pwd

    def check_pwd(self, pwd):
        '''
        Validate password string (must match settings)
        pwd (str) - password string

        Проверяет пароль на наличие необходимых символов из настроек
        '''

        if self.settings['has_extra'] and (self.settings['extra'] != ""):
            check_extra = True
        else:
            check_extra = False

        uppercase_ok = not self.settings['has_uppercase']
        lowercase_ok = not self.settings['has_lowercase']
        dig_ok = not self.settings['has_digits']
        spec_ok = not self.settings['has_special']
        extra_ok = not check_extra
        for ch in pwd:
            if not uppercase_ok and (ch in Password.ABC):
                uppercase_ok = True

            if not lowercase_ok and (ch in Password.abc):
                lowercase_ok = True

            if not dig_ok and (ch in Password.dig):
                dig_ok = True

            if not spec_ok and (ch in Password.spec):
                spec_ok = True

            if not extra_ok and (ch in self.settings['extra']):
                extra_ok = True

        return (uppercase_ok and lowercase_ok and dig_ok and spec_ok and extra_ok)
