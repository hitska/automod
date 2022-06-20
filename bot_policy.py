from post import Post


def get_policy(policy: str):
    policies = policy.split(' ')
    if not policies:
        raise Exception('Bot policy is not set')

    composite = BotPolicyComposite()
    for policy in policies:
        if policy == 'anonymous':
            composite.add(BotPolicyAnonimous())
        elif policy == 'blacklist':
            composite.add(BotPolicyBlackList())
        elif policy == 'whitelist':
            composite.add(BotPolicyWhiteList())
        elif policy == 'custom':
            composite.add(BotPolicyCustom())
        elif policy == 'not_anonymous':
            composite.add(BotPolicyNotAnonimous())
        else:
            raise Exception(f'Unknown bot policy: {policy}')
    return composite


class BotPolicyWhiteList:
    '''
    Трём всё кроме белого списка трипкодов (имена может кто угодно юзать) и, естественно, модераторов треда.
    '''
    def is_post_allowed(self, post, settings):
        if post.trip in settings['rules']['moderators']:
            return True
        if post.trip in settings['rules']['whitelist']:
            return True
        return False


class BotPolicyBlackList:
    '''
    Не трём ничего кроме чёрного списка.
    '''
    def is_post_allowed(self, post, settings):
        if post.trip in settings['rules']['blacklist']:
            return False
        return True


class BotPolicyAnonimous:
    '''
    Трёт ананим лигивон.
    '''
    def is_post_allowed(self, post, settings):
        if not post.trip and not post.images and post.name == 'Аноним':
            return False
        return True


class BotPolicyNotAnonimous:
    '''
    Трёт вниманиеблядей.
    '''
    def is_post_allowed(self, post, settings):
        if post.trip or post.name != 'Аноним':
            return False
        return True


class BotPolicyCustom:
    '''
    Трёт в соответствии с регексом в rules/custom.
    '''
    def is_post_allowed(self, post, settings):
        # TODO
        return True


class BotPolicyComposite:
    def __init__(self):
        self.policies = []

    def add(self, policy):
        self.policies.append(policy)

    def is_post_allowed(self, post, settings):
        for policy in self.policies:
            if not policy.is_post_allowed(post, settings):
                return False

        return True
