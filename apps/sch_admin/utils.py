def schDishes_jwt_respose_payload_handle(token, user=None, request=None):
    """
    自定义jwt认证成功，放回数据
    :param token:
    :param user:
    :param request:
    :return:
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }