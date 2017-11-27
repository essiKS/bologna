from channels.routing import route
from .consumers import dir_ws_message, dir_ws_connect, dir_ws_disconnect, dir_work_connect, dir_work_disconnect, dir_work_message
from otree.channels.routing import channel_routing
from channels.routing import include, route_class

dir_auction_path = r'^/(?P<group_name>\w+)$'
dir_work_path = r'^/(?P<worker_code>\w+)/(?P<player_pk>\w+)$'
directauction_routing = [route("websocket.connect",
                             dir_ws_connect, path=dir_auction_path),
                       route("websocket.receive",
                             dir_ws_message, path=dir_auction_path),
                       route("websocket.disconnect",
                             dir_ws_disconnect, path=dir_auction_path), ]

dir_workpage_routing = [route("websocket.connect",
                          dir_work_connect, path=dir_work_path),
                    route("websocket.receive",
                          dir_work_message, path=dir_work_path),
                    route("websocket.disconnect",
                          dir_work_disconnect, path=dir_work_path), ]

channel_routing += [
    include(directauction_routing, path=r"^/directauction"),
    include(dir_workpage_routing, path=r"^/dirworkpage"),
]
