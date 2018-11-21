import pygame
from pygame.locals import *
import datetime
import numpy as np
import pickle
import pulp
from game import game
from os import listdir, remove
from other_school import make_school
from shutil import rmtree
from collections import defaultdict
from classes import *

[STRAIGHT, SLIDER, CURVE, FORK, SINKER, SHOOT, H_SLIDER, CUT, SLOW_CURVE, DROP_CURVE, SLERVE, KNUCKLE_CURVE, V_SLIDER, PALM, 
SFF, CHANGEUP, H_SINKER, CIRCLE_CHANGE, H_SHOOT] = list(range(19))

[TOP, MENU, TRAINING, TRAININGSTART, CHALLENGE1, CHALLENGE2, VARIOUS, REGISTER, ORDER_POSITION, PLAYERS2, PLAYERS3, POLICY, SHOULDER_REGISTER, 
PLAYERS, SCOUT1, SCOUT4, EX_GAME, MY_ORDER, RIVAL_ORDER, GAME_RESULT, BAT_RESULTS, PITCH_RESULTS, CONFIRM, 
OTHER_SCHOOL, SCHOOL_LIST, ABILITYS, SIMULATION, CHOICE_SCHOOL, SCHOOL_LIST2, 
RIVAL_ORDER2, RIVAL_ORDER3] = list(range(31))

[HOKKAIDO, AOMORI, AKITA, YAMAGATA, IWATE, MIYAGI, HUKUSHIMA, NIGATA, TOYAMA, ISHIKAWA, HUKUI, NAGANO, GIHU, YAMANASHI, SHIZUOKA,
AITI, IBARAKI, TIBA, GUNMA, TOTIGI, SAITAMA, KANAGAWA, TOKYO, SHIGA, MIE, HYOGO, KYOTO, OSAKA, NARA, WAKAYAMA, TOTTORI, SHIMANE, 
OKAYAMA, HIROSHIMA, YAMAGUTI, KAGAWA, TOKUSHIMA, EHIME, KOTI, HUKUOKA, OITA, SAGA, NAGASAKI, KUMAMOTO, MIYAZAKI, KAGOSHIMA, OKINAWA, 
HIGASHITOKYO, NISHITOKYO, KITAHOKKAIDO, MINAMIHOKKAIDO] = list(range(51))

SCR_RECT = Rect(0, 0, 1181, 665)

# -------------------------------------------------------------
class Main:
    def __init__(self):
        self.players = self.read_players()
        self.rival_players = {}
        self.game_state = TOP
        [self.idx, self.school_data, self.ranks, self.study, self.choiced_name, self.player_idx, 
        self.choiced_ID, self.clicked_order] = [0, {}, {}, {}, '', 0, None, None]
        self.pos_names = {1: '投', 2: '捕', 3: '一', 4: '二', 5: '三', 6: '遊', 7: '左', 8: '中', 9: '右'}
        self.f = lambda a, x, Y, X: a * x + (Y - a * X)
        self.Max_transform = lambda x: self.f(14/85, x, 1, 80) if x <= 165 else 15
        self.staconpow_transform = lambda x: self.f(14/140, x, 1, 10) if x <= 150 else 15
        self.amount_transform = lambda x: x if x <= 15 else 15
        self.shoulder_number, self.order_number, self.position_number = [None]*3
        self.non_choiced, self.choiced, self.orders, self.positions, self.my_school = set(self.players.keys()), {}, {}, {}, '広島東洋カープ'
        self.rival_orders, self.rival_positions, self.rival_school = {}, {}, '福岡ソフトバンクホークス'
        self.school, self.my_attack = {}, True
        self.pitch_results, self.bat_results, self.front_back, self.bat_results_idx = {}, {}, 0, 0
        self.none = False
        self.score_list, self.Nhits, self.Nerrors = {}, {}, {}
        self.choiced_idx = 0
        self.choiced_names = [None, None]
        self.rival1_players, self.rival1_orders, self.rival1_positions = {}, {}, {}
        self.rival2_players, self.rival2_orders, self.rival2_positions = {}, {}, {}
        if 'studies_data.pickle' in listdir('data'):
            with open('data/studies_data.pickle', 'rb') as f: self.mu, self.std = pickle.load(f)
        if 'choiced.pickle' in listdir('data'):
            with open('data/choiced.pickle', 'rb') as f: self.choiced = pickle.load(f)
        if 'non_choiced.pickle' in listdir('data'):
            with open('data/non_choiced.pickle', 'rb') as f: self.non_choiced = pickle.load(f)
        if 'orders.pickle' in listdir('data'):
            with open('data/orders.pickle', 'rb') as f: self.orders = pickle.load(f)
        if 'positions.pickle' in listdir('data'):
            with open('data/positions.pickle', 'rb') as f: self.positions = pickle.load(f)
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption('高校野球シミュレーション')
        date.init_date(date)
        self.image, self.buttons, self.img_pos = Image(), Buttons(), Img_Pos()
        self.choiced_items = [self.buttons.items[i, 1].xywh for i in range(7)]
        clock = pygame.time.Clock()
        while True:
            tPassed = clock.tick(60)
            self.draw(screen)
            self.update(screen, tPassed/1000)
            pygame.display.update()
            self.key_handler()

    def update(self, screen, tPassed): # 投球動作や打球アニメーションを動かす予定
        if self.game_state == TRAININGSTART:
            vx = 1500
            if self.img_pos.pawa01.x <= 300:
                self.img_pos.pawa01.x += vx*tPassed
                if self.img_pos.pawa01.x > 300: self.img_pos.pawa01.x = 300
            screen.blit(self.image.pawa01, self.img_pos.pawa01)
            if self.img_pos.pawa01.x == 300 and self.img_pos.pawa02.x >= 630:
                self.img_pos.pawa02.x -= vx*tPassed
                if self.img_pos.pawa02.x < 630: self.img_pos.pawa02.x = 630
                screen.blit(self.image.pawa02, self.img_pos.pawa02)

    def draw(self, screen):
        if self.game_state == TOP:
            screen.blit(self.image.top, SCR_RECT.topleft)

        elif self.game_state == CONFIRM:
            screen.blit(self.image.confirm, SCR_RECT.topleft)

        elif self.game_state == MENU:
            screen.blit(self.image.menu, SCR_RECT.topleft)
            screen.blit(date.dateText, date.fontsize)

        elif self.game_state == OTHER_SCHOOL:
            screen.blit(self.image.other_school, SCR_RECT.topleft)

        elif self.game_state in (SCHOOL_LIST, SCHOOL_LIST2):
            screen.blit(self.image.school_list, SCR_RECT.topleft)
            if len(self.school_data) > self.idx + 24: screen.blit(self.image.next_img, self.buttons.next2.xy) # 次へ描画
            for i, name in enumerate(sorted(self.school_data)[self.idx: self.idx + 24]):
                self.blit_text(screen, 20, name, self.img_pos.name_pos[i])
                rank = self.ranks[name]
                text, color = self.ability_ranks(rank, 1)
                self.blit_text(screen, 30, text, self.img_pos.rank_pos[i], color=color, center=True, bold=True)
                self.blit_text(screen, 20, str(self.study[name]), self.img_pos.deviation_pos[i])

        elif self.game_state == ABILITYS:
            screen.blit(self.image.ability, SCR_RECT.topleft)
            self.blit_text(screen, 40, self.choiced_name, (588, 63))
            school = self.school_data[self.choiced_name]
            if len(school) > self.player_idx + 26: screen.blit(self.image.next_img, self.buttons.next2.xy) # 次へ描画
            for i, ID in enumerate(sorted(school)[self.player_idx: self.player_idx + 26]):
                pos = self.get_positions(school[ID])
                icon = pygame.transform.smoothscale(self.image.player_icons[pos], (144, 41)) # ポジションアイコンのサイズを調整
                screen.blit(icon, icon.get_rect(center=self.img_pos.players_pos[i]))
                self.blit_text(screen, 20, school[ID]['name'], self.img_pos.players_pos[i])
            if self.choiced_ID != None:
                player = school[self.choiced_ID]
                self.draw_ability(screen, player, (291, 118), (606, 134), 40, (750, 192), 20, self.img_pos.ability_pos)

        elif self.game_state == TRAINING:
            screen.blit(self.image.training, SCR_RECT.topleft)
            screen.blit(date.dateText, date.fontsize)

        elif self.game_state == TRAININGSTART:
            screen.blit(self.image.training_start, SCR_RECT.topleft)
            if self.img_pos.pawa02.x == 630:
                screen.blit(self.image.finish_training, self.img_pos.finish_training)
                screen.blit(self.image.tomorrow, self.img_pos.tomorrow)

        elif self.game_state == EX_GAME:
            screen.blit(self.image.ex_game, SCR_RECT.topleft)

        elif self.game_state in (MY_ORDER, RIVAL_ORDER, RIVAL_ORDER2, RIVAL_ORDER3):
            if self.game_state == MY_ORDER and (len(self.orders) != 9 or len(self.positions) != 9):
                screen.blit(self.image.trans_register, SCR_RECT.topleft)
            else:
                screen.blit(self.image.my_order, SCR_RECT.topleft)
                if self.game_state == MY_ORDER: school_name, orders, players, positions = self.my_school, self.orders, self.players, self.positions
                elif self.game_state == RIVAL_ORDER: school_name, orders, players, positions = self.rival_school, self.rival_orders, self.rival_players, self.rival_positions
                elif self.game_state == RIVAL_ORDER2: school_name, orders, players, positions = self.choiced_names[0], self.rival1_orders, self.rival1_players, self.rival1_positions
                elif self.game_state == RIVAL_ORDER3: school_name, orders, players, positions = self.choiced_names[1], self.rival2_orders, self.rival2_players, self.rival2_positions
                self.blit_text(screen, 40, school_name, (593, 63), color=(255, 0, 0))
                for number, ID in orders.items(): # 登録済み選手表示
                    player = players[ID]
                    pos = self.get_positions(player)
                    order_buttons = self.buttons.order_buttons[number] # 打順アイコンの位置、サイズ取得
                    icon = pygame.transform.smoothscale(self.image.player_icons[pos], (order_buttons.w, order_buttons.h)) # ポジションアイコンのサイズを打順アイコンに合わせる。
                    screen.blit(icon, (order_buttons.x, order_buttons.y)) # ポジションアイコンを打順部分に表示
                    self.blit_text(screen, 30, player['name'], (order_buttons.x + order_buttons.w / 2, order_buttons.y + order_buttons.h / 2))
                for number, p in positions.items():
                    position_buttons = self.buttons.position_buttons[number]
                    icon = self.image.pos_icon[p]
                    screen.blit(icon, (position_buttons.x, position_buttons.y))
                if self.game_state in (RIVAL_ORDER2, RIVAL_ORDER3) and self.clicked_order != None:
                    clicked_idx = 0 if self.clicked_order <= 5 else 1
                    screen.blit(self.image.ability_img, self.img_pos.ability_img_pos[clicked_idx])
                    player = self.rival1_players[self.rival1_orders[self.clicked_order]] if self.game_state == RIVAL_ORDER2 else self.rival2_players[self.rival2_orders[self.clicked_order]]
                    self.draw_ability(screen, player, (189, 81), ((761, 125), (225, 125))[clicked_idx], 30, ((856, 164), (320, 164))[clicked_idx], 15, self.img_pos.ability_pos2[clicked_idx])

        elif self.game_state == CHALLENGE1:
            screen.blit(self.image.apply, SCR_RECT.topleft)

        elif self.game_state == CHALLENGE2:
            screen.blit(self.image.challenge2, SCR_RECT.topleft)

        elif self.game_state == GAME_RESULT:
            school_name_x = 173
            screen.blit(self.image.score_image, SCR_RECT.topleft)
            self.blit_text(screen, 20, self.school[0], (school_name_x, self.img_pos.round_posy[0]), (255, 255, 0))
            self.blit_text(screen, 20, self.school[1], (school_name_x, self.img_pos.round_posy[1]), (255, 255, 0))
            for i, scores in self.score_list.items():
                for r, s in enumerate(scores): self.blit_text(screen, 30, str(s), (self.img_pos.round_posx[r], self.img_pos.round_posy[i]), (255, 255, 255), bold=True)
                for j in range(r + 1, 15): self.blit_text(screen, 40, '×', (self.img_pos.round_posx[j], self.img_pos.round_posy[i]), (255, 255, 255))
            self.blit_text(screen, 30, str(sum(self.score_list[0])), (self.img_pos.round_posx[-3], self.img_pos.round_posy[0]), (255, 255, 255), bold=True) # 先行の合計
            self.blit_text(screen, 30, str(sum(self.score_list[1])), (self.img_pos.round_posx[-3], self.img_pos.round_posy[1]), (255, 255, 255), bold=True) # 後攻の合計
            self.blit_text(screen, 30, str(self.Nhits[0]), (self.img_pos.round_posx[-2], self.img_pos.round_posy[0]), (255, 255, 255), bold=True) # 先行のヒット数
            self.blit_text(screen, 30, str(self.Nhits[1]), (self.img_pos.round_posx[-2], self.img_pos.round_posy[1]), (255, 255, 255), bold=True) # 後攻のヒット数
            self.blit_text(screen, 30, str(self.Nerrors[0]), (self.img_pos.round_posx[-1], self.img_pos.round_posy[0]), (255, 255, 255), bold=True) # 先行のエラー数
            self.blit_text(screen, 30, str(self.Nerrors[1]), (self.img_pos.round_posx[-1], self.img_pos.round_posy[1]), (255, 255, 255), bold=True) # 後攻のエラー数

            school_results = self.buttons.school_results[0]
            self.blit_text(screen, 40, self.school[0] + ' 投手成績', (school_results.x + school_results.w / 2, school_results.y + school_results.h / 2), (0, 0, 0))
            school_results = self.buttons.school_results[1]
            self.blit_text(screen, 40, self.school[0] + ' 野手成績', (school_results.x + school_results.w / 2, school_results.y + school_results.h / 2), (0, 0, 0))
            school_results = self.buttons.school_results[2]
            self.blit_text(screen, 40, self.school[1] + ' 投手成績', (school_results.x + school_results.w / 2, school_results.y + school_results.h / 2), (0, 0, 0))
            school_results = self.buttons.school_results[3]
            self.blit_text(screen, 40, self.school[1] + ' 野手成績', (school_results.x + school_results.w / 2, school_results.y + school_results.h / 2), (0, 0, 0))

        elif self.game_state == BAT_RESULTS:
            screen.blit(self.image.bat_results_img, SCR_RECT.topleft)
            bat_results = self.bat_results[self.front_back]
            if self.bat_results_idx == 0 and len(bat_results) > 9: # 試合に１０人以上出たら、次のページに表示
                screen.blit(self.image.next_img, self.buttons.next2.xy)
            keys = sorted(bat_results)[self.bat_results_idx: self.bat_results_idx + 9]
            if self.my_attack and self.front_back == 0:
                if None in self.choiced_names:
                    players = self.players
                else: players = self.rival1_players
            elif self.my_attack:
                if None in self.choiced_names:
                    players = self.rival_players
                else: players = self.rival2_players
            elif self.front_back == 0:
                if None in self.choiced_names:
                    players = self.rival_players
                else: players = self.rival2_players
            else:
                if None in self.choiced_names:
                    players = self.players
                else: players = self.rival1_players
            for i, ID in enumerate(keys):
                self.blit_text(screen, 20, players[ID]['name'], self.img_pos.bat_records[i][0])
                for j, value in enumerate(bat_results[ID]): self.blit_text(screen, 20, str(value), self.img_pos.bat_records[i][j+1])

        elif self.game_state == PITCH_RESULTS:
            screen.blit(self.image.pitch_results_img, SCR_RECT.topleft)
            pitch_results = self.pitch_results[self.front_back]
            if self.my_attack and self.front_back == 0:
                if None in self.choiced_names:
                    players = self.players
                else:
                    players = self.rival1_players
            elif self.my_attack:
                if None in self.choiced_names:
                    players = self.rival_players
                else: players = self.rival2_players
            elif self.front_back == 0:
                if None in self.choiced_names:
                    players = self.rival_players
                else: players = self.rival2_players
            else:
                if None in self.choiced_names:
                    players = self.players
                else: players = self.rival1_players
            for i, ID in enumerate(pitch_results):
                self.blit_text(screen, 30, players[ID]['name'], self.img_pos.pitch_records[i][0])
                for j, value in enumerate(pitch_results[ID]):
                    if j >= 3: j += 1
                    self.blit_text(screen, 30, str(value), self.img_pos.pitch_records[i][j+1])

        elif self.game_state == SIMULATION:
            screen.blit(self.image.simu_img, SCR_RECT.topleft)
            if self.choiced_names[0] != None: # 高校１が登録されている
                screen.blit(self.image.label_img, (152, 237))
                self.blit_text(screen, 60, self.choiced_names[0], (590, 311), (255, 255, 255))
            if self.choiced_names[1] != None: # 高校２が登録されている
                screen.blit(self.image.label_img, (152, 486))
                self.blit_text(screen, 60, self.choiced_names[1], (590, 563), (255, 255, 255))
            if None not in self.choiced_names:
                screen.blit(self.image.next_img, self.buttons.next4.xy)

        elif self.game_state == CHOICE_SCHOOL:
            screen.blit(self.image.other_school, SCR_RECT.topleft)

        elif self.game_state == VARIOUS:
            screen.blit(self.image.various, SCR_RECT.topleft)

        elif self.game_state == REGISTER:
            screen.blit(self.image.register, SCR_RECT.topleft)

        elif self.game_state == SHOULDER_REGISTER:
            screen.blit(self.image.shoulder_register, SCR_RECT.topleft)
            for number, ID in self.choiced.items(): # 登録済み選手表示
                player = self.players[ID]
                pos = self.get_positions(player)
                number_buttons = self.buttons.number_buttons[number] # 背番号アイコンの位置、サイズ取得
                icon = pygame.transform.smoothscale(self.image.player_icons[pos], (number_buttons.w, number_buttons.h)) # ポジションアイコンのサイズを背番号アイコンに合わせる。
                screen.blit(icon, (number_buttons.x, number_buttons.y)) # ポジションアイコンを背番号部分に表示
                self.blit_text(screen, 30, player['name'], (number_buttons.x + number_buttons.w / 2, number_buttons.y + number_buttons.h / 2))

        elif self.game_state == PLAYERS:
            screen.blit(self.image.non_choiced, SCR_RECT.topleft)
            self.blit_text(screen, 50, '背番号登録', (595, 67), color=(255, 255, 0))
            n = len(self.non_choiced)
            for i, ID in enumerate(sorted(self.non_choiced)): # 未登録選手一覧表示（選手が多いと次のページにいかせる実装はまだ）
                player = self.players[ID]
                pos = self.get_positions(player)
                icon, icon_pos = self.image.player_icons[pos], self.buttons.icon_pos[i] # ポジションアイコンの取得、表示場所の取得
                screen.blit(icon, (icon_pos.x, icon_pos.y)) # ポジションアイコン表示
                self.blit_text(screen, 30, player['name'], (icon_pos.x + icon_pos.w / 2, icon_pos.y + icon_pos.h / 2))
            screen.blit(self.image.none_img, (self.buttons.icon_pos[n].x, self.buttons.icon_pos[n].y)) # 登録なしを表示
            self.none = True # 登録なしを表示しているならTrue

        elif self.game_state == ORDER_POSITION:
            screen.blit(self.image.order_position, SCR_RECT.topleft)
            for number, ID in self.orders.items(): # 登録済み選手表示
                player = self.players[ID]
                pos = self.get_positions(player)
                order_buttons = self.buttons.order_buttons[number] # 打順アイコンの位置、サイズ取得
                icon = pygame.transform.smoothscale(self.image.player_icons[pos], (order_buttons.w, order_buttons.h)) # ポジションアイコンのサイズを打順アイコンに合わせる。
                screen.blit(icon, (order_buttons.x, order_buttons.y)) # ポジションアイコンを打順部分に表示
                self.blit_text(screen, 30, player['name'], (order_buttons.x + order_buttons.w / 2, order_buttons.y + order_buttons.h / 2))
            for number, p in self.positions.items():
                position_buttons = self.buttons.position_buttons[number]
                icon = self.image.pos_icon[p]
                screen.blit(icon, (position_buttons.x, position_buttons.y))

        elif self.game_state == PLAYERS2:
            screen.blit(self.image.non_choiced, SCR_RECT.topleft)
            self.blit_text(screen, 50, '打順・守備登録', (595, 67), color=(255, 255, 0))
            n = len(self.choiced) - len(self.orders)
            i = 0
            for ID in sorted(self.choiced.values()): # 登録済み選手表示
                if ID in self.orders.values(): continue
                player = self.players[ID]
                pos = self.get_positions(player)
                icon, icon_pos = self.image.player_icons[pos], self.buttons.icon_pos[i] # ポジションアイコンの取得、表示場所の取得
                screen.blit(icon, (icon_pos.x, icon_pos.y)) # ポジションアイコン表示
                self.blit_text(screen, 30, player['name'], (icon_pos.x + icon_pos.w / 2, icon_pos.y + icon_pos.h / 2))
                i += 1
            screen.blit(self.image.none_img, (self.buttons.icon_pos[n].x, self.buttons.icon_pos[n].y)) # 登録なしを表示

        elif self.game_state == PLAYERS3:
            screen.blit(self.image.non_choiced, SCR_RECT.topleft)
            self.blit_text(screen, 50, '打順・守備登録', (595, 67), color=(255, 255, 0))
            n = 9 - len(self.positions)
            i = 0
            for p in sorted(self.image.pos_icon): # ポジションアイコン表示
                if p in self.positions.values(): continue
                icon, icon_pos = self.image.pos_icon[p], self.buttons.icon_pos[i] # ポジションアイコンの取得、表示場所の取得
                screen.blit(icon, (icon_pos.x, icon_pos.y)) # ポジションアイコン表示
                i += 1
            screen.blit(self.image.none_img, (self.buttons.icon_pos[n].x, self.buttons.icon_pos[n].y)) # 登録なしを表示

        elif self.game_state == POLICY:
            screen.blit(self.image.policy, SCR_RECT.topleft)
            for i in range(7): pygame.draw.rect(screen, (255, 0, 0), self.choiced_items[i], 5)

        elif self.game_state == SCOUT1:
            screen.blit(self.image.scout, SCR_RECT.topleft)

        elif self.game_state == SCOUT4:
            screen.blit(self.image.scout4, SCR_RECT.topleft)

    def key_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                with open('data/choiced.pickle', 'wb') as f: pickle.dump(self.choiced, f)
                with open('data/non_choiced.pickle', 'wb') as f: pickle.dump(self.non_choiced, f)
                with open('data/orders.pickle', 'wb') as f: pickle.dump(self.orders, f)
                with open('data/positions.pickle', 'wb') as f: pickle.dump(self.positions, f)
                self.end()

            if event.type == MOUSEBUTTONUP:
                x, y = event.pos
                if self.game_state == TOP:
                    if self.buttons.start.check(x, y):
                        if 'school_data' not in listdir('data'): make_school() # データを消した後、はじめる以外を選択するとエラー起きるかも
                        self.game_state = MENU
                    elif self.buttons.other_school_data.check(x, y): self.game_state = OTHER_SCHOOL
                    elif self.buttons.delete.check(x, y): self.game_state = CONFIRM

                elif self.game_state == CONFIRM:
                    if self.buttons.yes.check(x, y):
                        for file in ('choiced', 'non_choiced', 'orders', 'positions', 'studies_data'): remove('data/' + file + '.pickle')
                        rmtree('data/school_data')
                        self.game_state = TOP
                    elif self.buttons.no.check(x, y): self.game_state = TOP

                elif self.game_state == OTHER_SCHOOL:
                    if self.buttons.Re1.check(x, y): self.game_state = TOP
                    else: self.get_prefecture_list(x, y, SCHOOL_LIST)

                elif self.game_state == SCHOOL_LIST:
                    if self.buttons.Re2.check(x, y):
                        if self.idx != 0: self.idx -= 24
                        else: self.game_state = OTHER_SCHOOL
                    elif self.buttons.Re7.check(x, y):
                        self.idx = 0
                        self.game_state = OTHER_SCHOOL
                    elif len(self.school_data) > self.idx + 24 and self.buttons.next2.check(x, y): self.idx += 24
                    else:
                        for i, button in enumerate(self.buttons.name_buttons):
                            if button.check(x, y) and self.idx + i < len(self.school_data):
                                self.choiced_name = sorted(self.school_data)[self.idx + i]
                                self.player_idx = 0
                                self.choiced_ID = None
                                self.game_state = ABILITYS
                                break

                elif self.game_state == ABILITYS:
                    if self.buttons.Re5.check(x, y):
                        self.choiced_ID = None
                        if self.player_idx != 0: self.player_idx -= 26
                        else: self.game_state = SCHOOL_LIST
                    elif self.buttons.Re6.check(x, y):
                        self.choiced_ID = None
                        self.player_idx = 0
                        self.game_state = SCHOOL_LIST
                    elif len(self.school_data[self.choiced_name]) > self.player_idx + 26 and self.buttons.next2.check(x, y):
                        self.choiced_ID = None
                        self.player_idx += 26
                    else:
                        for i, button in enumerate(self.buttons.players_buttons):
                            if button.check(x, y) and self.player_idx + i < len(self.school_data[self.choiced_name]):
                                self.choiced_ID = sorted(self.school_data[self.choiced_name])[self.player_idx + i] # none部分でエラー起こりそう

                elif self.game_state == MENU:
                    if self.buttons.training.check(x, y): self.game_state = TRAINING
                    elif self.buttons.scout.check(x, y): self.game_state = SCOUT1
                    elif self.buttons.game.check(x, y): self.game_state = EX_GAME
                    elif self.buttons.data.check(x, y): self.game_state = VARIOUS
                    elif self.buttons.Re.check(x, y): self.game_state = TOP

                elif self.game_state == TRAINING:
                    if self.buttons.training_start.check(x, y): self.game_state = TRAININGSTART
                    elif self.buttons.Re3.check(x, y): self.game_state = MENU

                elif self.game_state == TRAININGSTART:
                    if self.buttons.tomorrow.check(x, y):
                        self.img_pos.pawa01, self.img_pos.pawa02 = Rect(-260, 270, 240, 335), Rect(1191, 270, 260, 309)
                        date.change_date(datetime.datetime(date.year, date.month, date.day) + datetime.timedelta(days=1), date)
                        self.game_state = MENU

                elif self.game_state == EX_GAME:
                    if self.buttons.Re10.check(x, y): self.game_state = MENU
                    elif self.buttons.game_start.check(x, y): self.game_state = MY_ORDER
                    elif self.buttons.apply.check(x, y): self.game_state = CHALLENGE1
                    elif self.buttons.simulation.check(x, y): self.choiced_names, self.choiced_idx, self.game_state = [None, None], 0, SIMULATION

                elif self.game_state == MY_ORDER:
                    if len(self.orders) == 9 and len(self.positions) == 9:
                        if self.buttons.Re2.check(x, y): self.game_state = EX_GAME
                        elif self.buttons.next2.check(x, y):
                            with open('data/hawks.pickle', 'rb') as f: self.rival_players = pickle.load(f)
                            self.rival_orders, self.rival_positions = self.auto_order_position(self.rival_players)
                            self.game_state = RIVAL_ORDER
                    else:
                        if self.buttons.trans.check(x, y): self.game_state = REGISTER
                        
                elif self.game_state == RIVAL_ORDER:
                    if self.buttons.Re2.check(x, y): self.game_state = MY_ORDER
                    elif self.buttons.next2.check(x, y):
                        myorders = [self.orders[number] for number in sorted(self.orders)]
                        mypositions = {p: self.orders[number] for number, p in self.positions.items()}
                        rivalorders = [self.rival_orders[number] for number in sorted(self.rival_orders)]
                        rivalpositions = {p: self.rival_orders[number] for number, p in self.rival_positions.items()}
                        r = np.random.randint(2)
                        if r == 0:
                            self.my_attack = True
                            self.score_list, self.Nhits, self.Nerrors, self.pitch_results, self.bat_results = game(self.players, myorders, mypositions, self.rival_players, rivalorders, rivalpositions, True)
                            self.school = {0: self.my_school, 1: self.rival_school}
                        else:
                            self.my_attack = False
                            self.score_list, self.Nhits, self.Nerrors, self.pitch_results, self.bat_results = game(self.rival_players, rivalorders, rivalpositions, self.players, myorders, mypositions, True)
                            self.school = {0: self.rival_school, 1: self.my_school}
                        self.game_state = GAME_RESULT

                elif self.game_state == CHALLENGE1:
                    if self.buttons.Re1.check(x, y): self.game_state = EX_GAME
                    else:
                        for prefecture in range(HOKKAIDO, OKINAWA + 1):
                            button = self.buttons.prefecture[prefecture]
                            if button.check(x, y):
                                self.game_state = CHALLENGE2
                                break

                elif self.game_state == CHALLENGE2:
                    if self.buttons.Re4.check(x, y): self.game_state = CHALLENGE1

                elif self.game_state == GAME_RESULT:
                    if self.buttons.next2.check(x, y):
                        self.choiced_names = [None, None]
                        self.game_state = MENU
                    else:
                        for i, button in enumerate(self.buttons.school_results):
                            if button.check(x, y):
                                if i < 2: self.front_back = 0
                                else: self.front_back = 1
                                if i % 2 == 0: self.game_state = PITCH_RESULTS
                                else:
                                    self.bat_results_idx = 0
                                    self.game_state = BAT_RESULTS
                                break

                elif self.game_state == PITCH_RESULTS:
                    if self.buttons.Re2.check(x, y): self.game_state = GAME_RESULT

                elif self.game_state == BAT_RESULTS:
                    if self.buttons.Re2.check(x, y): self.game_state = GAME_RESULT
                    elif len(self.bat_results[self.front_back]) > 9 and self.bat_results_idx == 0 and self.buttons.next2.check(x, y):
                        self.bat_results_idx = 9

                elif self.game_state == SIMULATION:
                    if self.buttons.Re11.check(x, y): self.game_state = EX_GAME
                    elif None not in self.choiced_names and self.buttons.next4.check(x, y):
                        self.rival1_orders, self.rival1_positions = self.auto_order_position(self.rival1_players)
                        self.rival2_orders, self.rival2_positions = self.auto_order_position(self.rival2_players)
                        self.game_state = RIVAL_ORDER2
                    else:
                        for i, button in enumerate(self.buttons.school_choices):
                            if button.check(x, y):
                                self.game_state = CHOICE_SCHOOL
                                self.choiced_idx = i
                                break

                elif self.game_state == RIVAL_ORDER2:
                    if self.buttons.Re2.check(x, y):
                        self.clicked_order = None
                        self.game_state = SIMULATION
                    elif self.buttons.next2.check(x, y):
                        self.clicked_order = None
                        self.game_state = RIVAL_ORDER3
                    else:
                        for order, button in self.buttons.order_buttons.items():
                            if button.check(x, y):
                                if self.clicked_order == order: self.clicked_order = None
                                else: self.clicked_order = order
                                break

                elif self.game_state == RIVAL_ORDER3:
                    if self.buttons.Re2.check(x, y):
                        self.clicked_order = None
                        self.game_state = RIVAL_ORDER2
                    elif self.buttons.next2.check(x, y):
                        self.clicked_order = None
                        myorders = [self.rival1_orders[number] for number in sorted(self.rival1_orders)]
                        mypositions = {p: self.rival1_orders[number] for number, p in self.rival1_positions.items()}
                        rivalorders = [self.rival2_orders[number] for number in sorted(self.rival2_orders)]
                        rivalpositions = {p: self.rival2_orders[number] for number, p in self.rival2_positions.items()}
                        self.make_condition(self.rival1_players)
                        self.make_condition(self.rival2_players)
                        r = np.random.randint(2)
                        if r == 0:
                            self.my_attack = True
                            self.score_list, self.Nhits, self.Nerrors, self.pitch_results, self.bat_results = game(self.rival1_players, myorders, mypositions, self.rival2_players, rivalorders, rivalpositions, True)
                            self.school = {0: self.choiced_names[0], 1: self.choiced_names[1]}
                        else:
                            self.my_attack = False
                            self.score_list, self.Nhits, self.Nerrors, self.pitch_results, self.bat_results = game(self.rival2_players, rivalorders, rivalpositions, self.rival1_players, myorders, mypositions, True)
                            self.school = {0: self.choiced_names[1], 1: self.choiced_names[0]}
                        self.game_state = GAME_RESULT
                    else:
                        for order, button in self.buttons.order_buttons.items():
                            if button.check(x, y):
                                if self.clicked_order == order: self.clicked_order = None
                                else: self.clicked_order = order
                                break

                elif self.game_state == CHOICE_SCHOOL:
                    if self.buttons.Re1.check(x, y): self.game_state = SIMULATION
                    else: self.get_prefecture_list(x, y, SCHOOL_LIST2)

                elif self.game_state == SCHOOL_LIST2:
                    if self.buttons.Re2.check(x, y):
                        if self.idx != 0: self.idx -= 24
                        else: self.game_state = CHOICE_SCHOOL
                    elif self.buttons.Re7.check(x, y):
                        self.idx = 0
                        self.game_state = CHOICE_SCHOOL
                    elif len(self.school_data) > self.idx + 24 and self.buttons.next2.check(x, y): self.idx += 24
                    else:
                        for i, button in enumerate(self.buttons.name_buttons):
                            if button.check(x, y) and self.idx + i < len(self.school_data):
                                name = sorted(self.school_data)[self.idx + i]
                                self.choiced_names[self.choiced_idx] = name
                                if self.choiced_idx == 0: self.rival1_players = self.get_shoulder_num(self.school_data[name]) # 高校１登録
                                else: self.rival2_players = self.get_shoulder_num(self.school_data[name]) # 高校２登録
                                self.game_state = SIMULATION
                                break

                elif self.game_state == VARIOUS:
                    if self.buttons.Re8.check(x, y): self.game_state = MENU
                    elif self.buttons.register.check(x, y): self.game_state = REGISTER
                    elif self.buttons.plan.check(x, y): self.game_state = MENU
                    elif self.buttons.policy.check(x, y): self.game_state = POLICY
                    elif self.buttons.player.check(x, y): self.game_state = MENU
                    elif self.buttons.result.check(x, y): self.game_state = MENU

                elif self.game_state == REGISTER:
                    if self.buttons.Re9.check(x, y): self.game_state = VARIOUS
                    elif self.buttons.shoulder_register.check(x, y): self.game_state = SHOULDER_REGISTER
                    elif self.buttons.order_position.check(x, y): self.game_state = ORDER_POSITION

                elif self.game_state == SHOULDER_REGISTER:
                    if self.buttons.Re2.check(x, y): self.game_state = REGISTER
                    else:
                        for number, button in self.buttons.number_buttons.items():
                            if button.check(x, y):
                                self.game_state = PLAYERS
                                self.shoulder_number = number
                                break

                elif self.game_state == PLAYERS:
                    if self.buttons.Re2.check(x, y): self.game_state = SHOULDER_REGISTER
                    else:
                        n = len(self.non_choiced)
                        for i, ID in enumerate(sorted(self.non_choiced)):
                            if self.buttons.icon_pos[i].check(x, y):
                                if self.shoulder_number in self.choiced: # 既に登録さてていた場合
                                    preID = self.choiced[self.shoulder_number] # 登録されていた選手ID
                                    self.non_choiced.add(preID) # 未選択に戻す
                                    if preID in self.orders.values(): # 元の選手が打順登録されていたら削除
                                        order_number = [order_number for order_number, ID in self.orders.items() if preID == ID][0]
                                        del(self.orders[order_number])
                                    if preID in self.positions.values(): # 元の選手が守備登録されていたら削除
                                        position_number = [position_number for position_number, ID in self.positions.items() if preID == ID][0]
                                        del(self.positions[position_number])
                                self.choiced[self.shoulder_number] = ID # 登録
                                self.non_choiced.remove(ID)
                                self.game_state = SHOULDER_REGISTER
                                break
                        if self.none and self.buttons.icon_pos[n].check(x, y): # 登録なしをクリックしたとき
                            if self.shoulder_number in self.choiced: # 選手が登録されていた場合
                                preID = self.choiced[self.shoulder_number] # 登録選手ID
                                self.non_choiced.add(preID) # 未登録へ
                                del(self.choiced[self.shoulder_number]) # 登録削除
                                if preID in self.orders.values(): # 元の選手が打順登録されていたら削除
                                    order_number = [order_number for order_number, ID in self.orders.items() if preID == ID][0]
                                    del(self.orders[order_number])
                                if preID in self.positions.values(): # 元の選手が守備登録されていたら削除
                                    position_number = [position_number for position_number, ID in self.positions.items() if preID == ID][0]
                                    del(self.positions[position_number])
                            self.game_state = SHOULDER_REGISTER # 背番号画面へ

                elif self.game_state == ORDER_POSITION:
                    if self.buttons.Re2.check(x, y): self.game_state = REGISTER
                    else:
                        for number, button in self.buttons.order_buttons.items():
                            if button.check(x, y):
                                self.game_state = PLAYERS2
                                self.order_number = number
                                break
                        for number, button in self.buttons.position_buttons.items():
                            if button.check(x, y):
                                self.game_state = PLAYERS3
                                self.position_number = number
                                break

                elif self.game_state == PLAYERS2:
                    if self.buttons.Re2.check(x, y): self.game_state = ORDER_POSITION
                    else:
                        n = len(self.choiced) - len(self.orders)
                        i = 0
                        for ID in sorted(self.choiced.values()):
                            if ID in self.orders.values(): continue
                            if self.buttons.icon_pos[i].check(x, y):
                                self.orders[self.order_number] = ID # 登録
                                self.game_state = ORDER_POSITION
                                break
                            i += 1
                        if self.buttons.icon_pos[n].check(x, y): # 登録なしをクリックしたとき
                            if self.order_number in self.orders: # 選手が登録されていた場合
                                del(self.orders[self.order_number]) # 登録削除
                            self.game_state = ORDER_POSITION # 背番号画面へ

                elif self.game_state == PLAYERS3:
                    if self.buttons.Re2.check(x, y): self.game_state = ORDER_POSITION
                    else:
                        n = 9 - len(self.positions)
                        i = 0
                        for p in sorted(self.image.pos_icon):
                            if p in self.positions.values(): continue
                            if self.buttons.icon_pos[i].check(x, y):
                                self.positions[self.position_number] = p # 登録
                                self.game_state = ORDER_POSITION
                                break
                            i += 1
                        if self.buttons.icon_pos[n].check(x, y): # 登録なしをクリックしたとき
                            if self.position_number in self.positions: # 選手が登録されていた場合
                                del(self.positions[self.position_number]) # 登録削除
                            self.game_state = ORDER_POSITION # 背番号画面へ

                elif self.game_state == POLICY:
                    if self.buttons.Re1.check(x, y): self.game_state = VARIOUS
                    else:
                        for (i, j), button in self.buttons.items.items():
                            if button.check(x, y):
                                self.choiced_items[i] = self.buttons.items[i, j].xywh
                                break

                elif self.game_state == SCOUT1:
                    if self.buttons.Re1.check(x, y): self.game_state = MENU
                    else:
                        for prefecture in range(HOKKAIDO, OKINAWA + 1):
                            button = self.buttons.prefecture[prefecture]
                            if button.check(x, y):
                                self.game_state = SCOUT4
                                break

                elif self.game_state == SCOUT4:
                    if self.buttons.Re4.check(x, y): self.game_state = SCOUT1

    def get_prefecture_list(self, x, y, game_state):
        for prefecture in range(HOKKAIDO, OKINAWA + 1):
            button = self.buttons.prefecture[prefecture]
            if button.check(x, y):
                self.idx = 0
                if prefecture == HOKKAIDO:
                    with open('data/school_data/schools{}.pickle'.format(KITAHOKKAIDO), 'rb') as f: self.school_data = pickle.load(f)
                    with open('data/school_data/schools{}.pickle'.format(MINAMIHOKKAIDO), 'rb') as f: self.school_data.update(pickle.load(f))
                elif prefecture == TOKYO:
                    with open('data/school_data/schools{}.pickle'.format(HIGASHITOKYO), 'rb') as f: self.school_data = pickle.load(f)
                    with open('data/school_data/schools{}.pickle'.format(NISHITOKYO), 'rb') as f: self.school_data.update(pickle.load(f))
                else:
                    with open('data/school_data/schools{}.pickle'.format(prefecture), 'rb') as f: self.school_data = pickle.load(f)
                self.get_school_rank_deviation()
                self.game_state = game_state
                break

    def get_school_rank_deviation(self):
        for name, data in self.school_data.items():
            team_status = []
            team_study = []
            for status in data.values():
                team_study.append(status['study'])
                if 1 in status['position']:
                    team_status.append(np.array([self.Max_transform(status['Max']), self.staconpow_transform(status['stamina']),
                        self.staconpow_transform(status['control']), self.amount_transform(status['amount'].sum()),
                        self.staconpow_transform(status['power']), status['meet'], status['run'], status['shoulder'], status['field']
                        ]).mean())
                else:
                    team_status.append(np.array([self.staconpow_transform(status['power']), status['meet'], 
                        status['run'], status['shoulder'], status['field']]).mean())
            team_study = (((np.array(team_study) - self.mu) / self.std) * 10 + 50).mean()
            self.ranks[name] = np.array(sorted(team_status, reverse=True)[:18]).mean()
            self.study[name] = int(team_study)

    def read_players(self):
        players = {
            1: {'name': '大瀬良', 'condition': np.random.randint(1, 6), 'stand': True, 'handedness': True, 'position': {1: 1}, 'meet': 1, 'power': 25, 'run': 6, 'shoulder': 11, 'field': 8, 'pass_error': 8, 
                        'Max': 150, 'stamina': 110, 'control': 140, 'breaking': [CUT, SLOW_CURVE, SFF], 'amount': np.array([4, 1, 3])},
            2: {'name': '會 澤', 'condition': np.random.randint(1, 6), 'stand': True, 'handedness': True, 'position': {2: 1}, 'meet': 10, 'power': 103, 'run': 6, 'shoulder': 11, 'field': 6, 'pass_error': 7, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            3: {'name': 'バティスタ', 'condition': np.random.randint(1, 6), 'stand': True, 'handedness': True, 'position': {3: 1, 7: 0.8}, 'meet': 6, 'power': 160,'run': 7, 'shoulder': 10, 'field': 4, 'pass_error': 4, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            4: {'name': '菊 池', 'condition': np.random.randint(1, 6), 'stand': True, 'handedness': True, 'position': {4: 1}, 'meet': 6, 'power': 99, 'run': 12, 'shoulder': 13, 'field': 15, 'pass_error': 12, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            5: {'name': '安 部', 'condition': np.random.randint(1, 6), 'stand': False, 'handedness': True, 'position': {3: 1}, 'meet': 11, 'power': 70,'run': 12, 'shoulder': 10, 'field': 10, 'pass_error': 6, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            6: {'name': '田 中', 'condition': np.random.randint(1, 6), 'stand': False, 'handedness': True, 'position': {6: 1}, 'meet': 8, 'power': 87, 'run': 13, 'shoulder': 9, 'field': 12, 'pass_error': 6, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            7: {'name': '野 間', 'condition': np.random.randint(1, 6), 'stand': False, 'handedness': True, 'position': {7: 1}, 'meet': 8, 'power': 70, 'run': 14, 'shoulder': 15, 'field': 11, 'pass_error': 11, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            8: {'name': '丸', 'condition': np.random.randint(1, 6), 'stand': False, 'handedness': True, 'position': {8: 1}, 'meet': 12, 'power': 140, 'run': 12, 'shoulder': 10, 'field': 13, 'pass_error': 10, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])},
            9: {'name': '鈴 木', 'condition': np.random.randint(1, 6), 'stand': True, 'handedness': True, 'position': {9: 1}, 'meet': 12, 'power': 138, 'run': 10, 'shoulder': 15, 'field': 8, 'pass_error': 5, 
                        'Max': 110, 'stamina': 30, 'control': 90, 'breaking': [], 'amount': np.array([])}
                        }
        return players

    def get_positions(self, player):
        icon = ''
        pos = player['position']
        if 1 in pos: icon += 'p'
        if 2 in pos: icon += 'c'
        if 3 in pos or 4 in pos or 5 in pos or 6 in pos: icon += 'i'
        if 7 in pos or 8 in pos or 9 in pos: icon += 'o'
        if len(icon) > 3:
            print('ポジションが多すぎる。 pos =', pos)
            exit()
        return icon

    def auto_order_position(self, players):
        problem = pulp.LpProblem("Problem", pulp.LpMaximize)
        x = {(ID, number): pulp.LpVariable('x{}_{}'.format(ID, number), 0, 1, 'Binary') for ID in players for number in range(1, 10)}
        cost = {}
        for ID in players:
            player = players[ID]
            for number in range(1, 10):
                c = 0
                if number in player['position']: c += player['position'][number]
                if number == 1:
                    c += (player['Max'] / (170*4) + player['stamina'] / (255*4) + player['control'] / (255*4) + player['amount'].sum() / (35*4))
                else:
                    c += (player['meet']/75 + player['power']*20/255/100 + player['run']/100 + player['shoulder']/100 + player['field']/100 + player['pass_error']/100)
                cost[ID, number] = c

        problem += pulp.lpSum([cost[ID, number] * x[ID, number] for ID in players for number in range(1, 10)])
        for ID in players:
            problem += pulp.lpSum([x[ID, number] for number in range(1, 10)]) <= 1
        for number in range(1, 10):
            problem += pulp.lpSum([x[ID, number] for ID in players]) == 1

        problem.solve()

        positions, orders = {}, {}
        ability = []
        for ID in players:
            for number in range(1, 10):
                if x[ID, number].value() == 1:
                    positions[ID] = number
                    ability.append((ID, players[ID]['meet'], players[ID]['power'], players[ID]['run']))
        ability = np.array(ability)

        # ４番
        idx = (ability[:,1] + ability[:,2]*15*4/255).argmax()
        orders[4] = int(ability[idx][0])
        ability = np.delete(ability, idx, axis=0)

        # ３番
        idx = (ability[:,1] + ability[:,2]*15/255).argmax()
        orders[3] = int(ability[idx][0])
        ability = np.delete(ability, idx, axis=0)

        # ５番
        idx = (ability[:,1] + ability[:,2]*15*4/255).argmax()
        orders[5] = int(ability[idx][0])
        ability = np.delete(ability, idx, axis=0)

        # １番
        idx = (ability[:,1] + ability[:,2]*15/255 + ability[:,3]).argmax()
        orders[1] = int(ability[idx][0])
        ability = np.delete(ability, idx, axis=0)

        # ２番
        idx = (ability[:,1] + ability[:,2]*15/255 + ability[:,3]).argmax()
        orders[2] = int(ability[idx][0])
        ability = np.delete(ability, idx, axis=0)

        for number, idx in zip(range(6, 10), (ability[:,1] + ability[:,2]*15/255).argsort()[::-1]):
            orders[number] = int(ability[idx][0])

        positions2 = {order: positions[ID] for order, ID in orders.items()}
        return orders, positions2

    def get_shoulder_num(self, players): # 投手以外はポジ無しが起こるかも
        abilities = defaultdict(list)
        for ID, status in players.items():
            if 1 in status['position']:
                ability = (np.array([self.Max_transform(status['Max']), self.staconpow_transform(status['stamina']),
                    self.staconpow_transform(status['control']), self.amount_transform(status['amount'].sum())])).mean()
                abilities[1].append((ID, ability))
            else:
                ability = (np.array([self.staconpow_transform(status['power']), status['meet'], 
                    status['run'], status['shoulder'], status['field']]).mean())
                abilities[2].append((ID, ability))
        rival_players = {}
        abilarray = np.array(abilities[1])
        indices = (-abilarray[:,1]).argsort()
        for ID in abilarray[:,0][indices][:5]: rival_players[ID] = players[ID]

        abilarray = np.array(abilities[2])
        indices = (-abilarray[:,1]).argsort()[:18 - len(rival_players)]
        for ID in abilarray[:,0][indices]: rival_players[ID] = players[ID]
        return rival_players

    def make_condition(self, players):
        for ID in players: players[ID]['condition'] = np.random.randint(1, 6)

    def blit_text(self, screen, size, text, text_pos, color=(0, 0, 0), bold=False, center=True):
        font = pygame.font.Font('IPAexfont00301/Meiryo.ttf', size)
        if bold: font.set_bold(True)
        Text = font.render(text, True, color)
        if center: text_pos = Text.get_rect(center=text_pos)
        screen.blit(Text, text_pos)

    def ability_ranks(self, rank, ver):
        ranks = ['G', 'F', 'E', 'D', 'C', 'B', 'A']
        colors = ((140, 140, 140), (0, 255, 255), (0, 255, 65), (255, 255, 0), (255, 195, 76), (255, 0, 0), (239, 117, 188))
        if ver == 1: abilities = np.array([4, 6, 8, 10, 12, 14, float('infinity')])
        elif ver == 2: abilities = np.array([20, 65, 80, 95, 110, 140, float('infinity')])
        elif ver == 3: abilities = np.array([15, 30, 60, 80, 110, 150, float('infinity')])
        else: abilities = np.array([100, 110, 120, 135, 155, 180, float('infinity')])
        idx = np.argmin(abilities <= rank)
        return ranks[idx], colors[idx]

    def draw_ability(self, screen, player, icon_size, icon_pos, name_size, name_pos, text_size, text_pos):
        pos = self.get_positions(player)
        icon = pygame.transform.smoothscale(self.image.player_icons[pos], icon_size) # ポジションアイコンのサイズを調整
        screen.blit(icon, icon_pos)
        self.blit_text(screen, name_size, player['name'], name_pos)
        self.blit_text(screen, text_size, str(player['grade']), text_pos[0])
        pos_connect = ''
        for p in sorted(player['position']): pos_connect += self.pos_names[p]
        self.blit_text(screen, text_size, pos_connect, text_pos[1])
        
        A = ('meet', 'power', 'run', 'shoulder', 'field', 'pass_error', 'Max', 'stamina', 'control')
        Ver = (1, 2, 1, 1, 1, 1, None, 3, 4)
        for a, ver, pos in zip(A, Ver, range(2, 11)):
            if a != 'Max': (text, color), bold = self.ability_ranks(player[a], ver), True
            else: text, color, bold = '{}km/h'.format(player[a]), (0, 0, 0), False # 球速
            self.blit_text(screen, text_size, text, text_pos[pos], color=color, center=True, bold=bold)

        if len(player['breaking']) > 1:
            for breaking, amount in zip(player['breaking'], player['amount']):
                self.blit_text(screen, text_size, str(amount), text_pos[self.img_pos.breaking_pos[breaking]])
        elif len(player['breaking']) == 1: self.blit_text(screen, text_size, str(player['amount'][0]), text_pos[self.img_pos.breaking_pos[player['breaking'][0]]])


    def end(self):
        pygame.quit()
        exit()
# -------------------------------------------------------------

date = GrobalDate()
Main()


