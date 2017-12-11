from channels.routing import route
from italianwage.consumers import ws_message, ws_connect, ws_disconnect, work_connect, work_disconnect, work_message
from italiandirect.consumers import dir_ws_message, dir_ws_connect, dir_ws_disconnect, dir_work_connect, \
    dir_work_disconnect, dir_work_message
from italiantutorial.consumers import tut_work_connect, tut_work_disconnect, tut_work_message, big_connect, \
    big_disconnect, big_message
from otree.channels.routing import channel_routing
from channels.routing import include, route_class

tut_answer_path = r'^/(?P<participant_code>\w+)$'
auction_path = r'^/(?P<group_name>\w+)$'
work_path = r'^/(?P<worker_code>\w+)/(?P<player_pk>\w+)$'
dir_auction_path = r'^/(?P<group_name>\w+)$'


tut_workpage_routing = [route("websocket.connect",
                          tut_work_connect, path=work_path),
                    route("websocket.receive",
                          tut_work_message, path=work_path),
                    route("websocket.disconnect",
                          tut_work_disconnect, path=work_path), ]

tut_answer_routing = [route("websocket.connect", big_connect, path=tut_answer_path),
                   route("websocket.receive", big_message, path=tut_answer_path),
                   route("websocket.disconnect", big_disconnect, path=tut_answer_path) ]


directauction_routing = [route("websocket.connect",
                             dir_ws_connect, path=dir_auction_path),
                       route("websocket.receive",
                             dir_ws_message, path=dir_auction_path),
                       route("websocket.disconnect",
                             dir_ws_disconnect, path=dir_auction_path), ]

dir_workpage_routing = [route("websocket.connect",
                          dir_work_connect, path=work_path),
                    route("websocket.receive",
                          dir_work_message, path=work_path),
                    route("websocket.disconnect",
                          dir_work_disconnect, path=work_path), ]

wageauction_routing = [route("websocket.connect",
                             ws_connect, path=auction_path),
                       route("websocket.receive",
                             ws_message, path=auction_path),
                       route("websocket.disconnect",
                             ws_disconnect, path=auction_path), ]

workpage_routing = [route("websocket.connect",
                          work_connect, path=work_path),
                    route("websocket.receive",
                          work_message, path=work_path),
                    route("websocket.disconnect",
                          work_disconnect, path=work_path), ]

channel_routing += [
    include(tut_answer_routing, path=r"^/questionnaire"),
    include(tut_workpage_routing, path=r"^/tutworkpage"),
    include(directauction_routing, path=r"^/directauction"),
    include(dir_workpage_routing, path=r"^/dirworkpage"),
    include(wageauction_routing, path=r"^/wageauction"),
    include(workpage_routing, path=r"^/workpage"),
]
