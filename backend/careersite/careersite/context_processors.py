def user_id(request):
    user_id = None
    if 'user_id' in request.session:
        user_id = request.session['user_id']

    return {'user_id': user_id}
