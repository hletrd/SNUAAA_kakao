from flask import Flask, request, Response, send_from_directory
import json
from konlpy.tag import Kkma
import time
import datetime
import requests
import random
import threading
import os
from secret import *

app = Flask(__name__)
kkma = Kkma()

seminar = ['2017-01-18', '2017-02-01', '2017-02-08', '2017-02-15', '2017-02-22', '2017-03-07', '2017-03-08', '2017-03-14', '2017-03-15', '2017-03-21', '2017-03-22', '2017-03-28', '2017-03-29', '2017-04-05', '2017-04-06', '2017-04-12', '2017-04-13', '2017-04-25', '2017-04-26', '2017-05-02', '2017-05-09', '2017-05-10', '2017-05-16', '2017-05-17', '2017-05-23', '2017-05-24', '2017-05-30', '2017-05-31', '2017-06-07', '2017-06-20', '2017-06-21']
days = ['일', '월', '화', '수', '목', '금', '토']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2979.0 Safari/537.36'}
fixed = "아직 답변이 준비되지 않은 단어입니다.\n\n지원하는 입력 예시:\n'끝말잇기 해요'\n'별모임이 언제인가요?'\n'겨울관측회가 어디에서 열리나요?'"

history = {}
wordchain = {}

last = {}

seminar_parsed = []
for i in seminar:
	seminar_parsed.append(time.strptime(i, "%Y-%m-%d"))

@app.route('/_images/<path:path>')
def send_static(path):
	return send_from_directory('images', path, as_attachment=False)

@app.route('/keyboard', methods=['GET'])
def keyboard():
	response = json.dumps({"type" : "text"})
	return Response(response, mimetype='application/json')

@app.route('/message', methods=['POST'])
def message():
	content = request.get_json(silent=True)
	if content['type'] == 'text':
		message = content['content']
		ukey = content['user_key']
		print(message)
		if len(message) > 500:
			response = json.dumps({"message": {"text": "너무 긴 메시지입니다."}})
		else:
			morphs = kkma.morphs(message)
			nouns = kkma.nouns(message)
			text = ''
			if ukey in last:
				last[ukey].insert(0, message)
			else:
				last[ukey] = [message]


			#다음 별모임 일자
			if '별모임' in nouns or '별모임' in morphs:
				if '언제' in morphs and '어디' in morphs:
					text = '다음 별모임은 '
					before = seminar_parsed[0]
					for i in seminar_parsed:
						if time.mktime(time.localtime()) - time.mktime(i) < 0:
							break
						before = i
					text += time.strftime("%m월 ", before).lstrip('0') + time.strftime("%d일 ", before).lstrip('0') + days[int(time.strftime("%w", before))] + '요일'
					text += ' 19시 30분에 학군단(66동) 옥상에 위치한 돔에서 열립니다.'
				elif '언제' in morphs:
					text = '다음 별모임은 '
					before = seminar_parsed[0]
					for i in seminar_parsed:
						if time.mktime(time.localtime()) - time.mktime(i) < 0:
							break
						before = i
					text += time.strftime("%m월 ", before).lstrip('0') + time.strftime("%d일 ", before).lstrip('0') + days[int(time.strftime("%w", before))] + '요일'
					text += ' 19시 30분에 열립니다. '
				elif '어디' in morphs:
					text = '별모임은 학군단(66동) 옥상에 위치한 돔에서 열립니다.'

			#겨관 일자
			elif '겨울' in nouns and '관측' in nouns or '겨관' in message:
				if '언제' in morphs and '어디' in morphs:
					text = '겨울관측회는 2월 10일 금요일부터 13일 월요일까지 충북 보은군 속리산면 사내리 283-2에 위치한 속리산 패밀리 펜션에서 열립니다.'
				elif '언제' in morphs:
					text = '겨울관측회는 2월 10일 금요일부터 13일 월요일까지입니다.'
				elif '어디' in morphs:
					text += '겨울관측회는 충북 보은군 속리산면 사내리 283-2에 위치한 속리산 패밀리 펜션에서 열립니다.'

			#반란군
			elif '반란군' in nouns and '놈' in nouns and '새끼' in nouns:
				text = ['니들 거기 꼼짝말고 있어!', '장세동이 바꾸라니깐!', '역적 놈의 새끼들...'][random.randint(0, 2)]
			
			#연락처
			elif '회장' in nouns and '연락처' in nouns:
				text = contacts[0]
			elif '부회장' in nouns and '연락처' in nouns:
				text = contacts[1]
			elif '총무' in nouns and '연락처' in nouns:
				text = contacts[2]
			elif '회계' in nouns and '연락처' in nouns:
				text = contacts[3]
			elif '관측부장' in nouns and '연락처' in nouns:
				text = contacts[4]
			elif ('별방' in nouns or '동아리방' in nouns) and '연락처' in nouns:
				text = '별방 전화번호는 02-874-9374입니다.'


			#이전 대화 잇기
			elif '언제' in nouns or '어디' in morphs:
				if len(last[ukey]) >= 2:
					lastnoun = kkma.nouns(last[ukey][1])
					if '겨관' in last[ukey][1] or ('겨울' in lastnoun and '관측회' in lastnoun):
						if '언제' in morphs and '어디' in morphs:
							text = '겨울관측회는 2월 10일 금요일부터 13일 월요일까지 충북 보은군 속리산면 사내리 283-2에 위치한 속리산 패밀리 펜션에서 열립니다.'
						elif '언제' in morphs:
							text = '겨울관측회는 2월 10일 금요일부터 13일 월요일까지입니다.'
						elif '어디' in morphs:
							text += '겨울관측회는 충북 보은군 속리산면 사내리 283-2에 위치한 속리산 패밀리 펜션에서 열립니다.'
					elif '별모임' in last[ukey][1]:
						if '언제' in morphs and '어디' in morphs:
							text = '다음 별모임은 '
							before = seminar_parsed[0]
							for i in seminar_parsed:
								if time.mktime(time.localtime()) - time.mktime(i) < 0:
									break
								before = i
							text += time.strftime("%m월 ", before).lstrip('0') + time.strftime("%d일 ", before).lstrip('0') + days[int(time.strftime("%w", before))] + '요일'
							text += ' 19시 30분에 학군단(66동) 옥상에 위치한 돔에서 열립니다.'
						elif '언제' in morphs:
							text = '다음 별모임은 '
							before = seminar_parsed[0]
							for i in seminar_parsed:
								if time.mktime(time.localtime()) - time.mktime(i) < 0:
									break
								before = i
							text += time.strftime("%m월 ", before).lstrip('0') + time.strftime("%d일 ", before).lstrip('0') + days[int(time.strftime("%w", before))] + '요일'
							text += ' 19시 30분에 열립니다. '
						elif '어디' in morphs:
							text = '별모임은 학군단(66동) 옥상에 위치한 돔에서 열립니다.'

			#날씨
			elif '날씨' in nouns:
				if '철원' in nouns:
					response = json.dumps({"message": {"text": "철원군의 날씨 예보입니다.", "photo": {"url": "http://0101010101.com:8002/_images/seeing-cherwon.png", "width": 1070, "height": 1826}}})

			#프사 시비
			elif '프사' in message or ('프로필' in nouns and '사진' in nouns):
				text = '좋은 프사 좀 만들어주세요...'

			#분석
			elif '분석' in nouns:
				text += "\n\n입력 분석 결과: " + str(morphs) + '\n' + str(nouns)

			#기타
			else:
				del last[ukey][0]
				text = fixed
			if text == '':
				del last[ukey][0]
				text = fixed
			response = json.dumps({"message": {"text": text}})
		return Response(response, mimetype='application/json')
	elif content['type'] == 'photo':
		response = json.dumps({"message": {"text": "아직 사진 수신은 지원하지 않습니다."}})
		return Response(response, mimetype='application/json')

@app.route('/friend', methods=['POST'])
def friend_post():
	return ''

@app.route('/friend/<user_key>', methods=['DELETE'])
def friend_delete(user_key):
	return ''

@app.route('/chat_room/<user_key>', methods=['DELETE'])
def chat_room(user_key):
	return ''

class capture(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while True:
			os.system('phantomjs seeing.js')
			time.sleep(1800)

if __name__ == '__main__':
	t = capture()
	t.start()
	app.run(host='0.0.0.0', port=8002)