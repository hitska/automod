from post import Post

def get_policy(policy: str):
    policies = policy.split(' ')
    if not policies:
        raise Exception('Bot policy is not set')

    composite = BotPolicyComposite()

    # Политики, критически важные для функционирования бота
    composite.add(BotPolicySaveByModList())
    composite.add(BotPolicySaveByPostNumber())

    for policy in policies:
        if policy == 'del-all':
            composite.add(BotPolicyDelAll())
        elif policy == 'whitelist':
            composite.add(BotPolicySaveByWhiteList())
        elif policy == 'blacklist':
            composite.add(BotPolicyDelByBlackList())
        elif policy == 'anonymous':
            composite.add(BotPolicyDelAnonimous())
        elif policy == 'not_anonymous':
            composite.add(BotPolicyDelNotAnonimous())
        elif policy == 'regex':
            composite.add(BotPolicyDelByRegexRules())
        else:
            raise Exception(f'Unknown bot policy: {policy}')
    return composite


class Resolution:
    CRITICAL_SAVE = 1001    # Для обеспечения функционирования бота
    HIGH_SAVE     = 101     # Для исключений
    HIGH_REMOVE   = 100     # Для исключений
    SAVE          = 11
    REMOVE        = 10
    NO_RESOLUTION = 1

    @staticmethod
    def is_post_allowed(resolution):
        if resolution % 2 == 0:
            return False
        return True


class BotPolicySaveByPostNumber:
    '''
    Сейвит посты, номера которых запрещено удалять.
    '''
    def is_post_allowed(self, post, settings):
        # Ни при каких обстоятельствах не трогаем посты до этого включительно
        if post.id <= settings['rules']['skip_posts_before']:
            return Resolution.CRITICAL_SAVE

        return Resolution.NO_RESOLUTION


class BotPolicySaveByModList:
    '''
    Сейвит модераторов по их трипкодам.
    '''
    def is_post_allowed(self, post, settings):
        if post.trip in settings['moderators']:
            return Resolution.CRITICAL_SAVE

        return Resolution.NO_RESOLUTION


class BotPolicySaveByWhiteList:
    '''
    Сейвит "белый список" трипкодов или имён.
    Имеет более высокий приоритет, чем операции удаления, поэтому работает как список исключений.
    '''
    def __init__(self):
        self.names = None
        self.trips = None

    def is_post_allowed(self, post, settings):
        if not self.names or not self.trips:
            self.names = set()
            self.trips = set()

            for name_or_tripcode in settings['rules']['whitelist']:
                if name_or_tripcode[:1] == '!':
                    self.trips.add(name_or_tripcode)
                else:
                    self.names.add(name_or_tripcode)

        if (post.trip in self.trips) or (post.name in self.names):
            return Resolution.HIGH_SAVE

        return Resolution.NO_RESOLUTION


class BotPolicyDelByBlackList:
    '''
    Удаляет "чёрный список" трипкодов или имён.
    '''

    def __init__(self):
        self.names = None
        self.trips = None

    def is_post_allowed(self, post, settings):
        if not self.names or not self.trips:
            self.names = set()
            self.trips = set()

            for name_or_tripcode in settings['rules']['blacklist']:
                if name_or_tripcode[:1] == '!':
                    self.trips.add(name_or_tripcode)
                else:
                    self.names.add(name_or_tripcode)

        if (post.trip in self.trips) or (post.name in self.names):
            return Resolution.HIGH_REMOVE

        return Resolution.NO_RESOLUTION


class BotPolicyDelAnonimous:
    '''
    Удаляет ананим лигивон, не трогает посты с картинками.
    Имеет низкий приоритет.
    '''
    def is_post_allowed(self, post, settings):
        if not post.trip and not post.images and post.name == 'Аноним':
            return Resolution.REMOVE

        return Resolution.NO_RESOLUTION


class BotPolicyDelNotAnonimous:
    '''
    Удаляет вниманиеблядей, не трогает посты с картинками.
    Имеет низкий приоритет.
    '''
    def is_post_allowed(self, post, settings):
        if post.trip or post.name != 'Аноним':
            return Resolution.REMOVE

        return Resolution.NO_RESOLUTION


class BotPolicyDelByRegexRules:
    '''
    Удаляет в соответствии с регексом в rules/regex.
    Имеет низкий приоритет.
    '''
    def is_post_allowed(self, post, settings):
        # TODO
        if False:
            return Resolution.REMOVE
        return Resolution.NO_RESOLUTION


class BotPolicyDelAll:
    '''
    Удаляет вообще всё.
    Имеет низкий приоритет.
    '''
    def is_post_allowed(self, post, settings):
        return Resolution.REMOVE


class BotPolicyComposite:
    def __init__(self):
        self.policies = []

    def add(self, policy):
        self.policies.append(policy)

    def is_post_allowed(self, post, settings):
        final_resolution = Resolution.NO_RESOLUTION

        for policy in self.policies:
            resolution = policy.is_post_allowed(post, settings)
            if resolution > final_resolution:
                final_resolution = resolution

        return Resolution.is_post_allowed(final_resolution)
