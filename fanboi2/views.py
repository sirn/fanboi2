def root_view(request):
    boards = request.context.objs
    return locals()


def board_view(request):
    boards = request.context.__parent__.objs
    board = request.context
    return locals()