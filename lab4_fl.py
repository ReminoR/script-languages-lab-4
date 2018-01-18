from threading import Thread
from bs4 import BeautifulSoup
import requests
from queue import Queue
import time
import re

# 1. Получаем html-код страницы
# 2. Собираем новостную информацию
# 3. Добавляем информацию в очередь
# 4. Берем из очереди и печатаем в консоль



def get_html(url, q):
	all_titles = set() #для id новостей
	id_post = 0

	while True:
		r = requests.get(url).text
		soup = BeautifulSoup(r, 'html5lib')
		container = soup.find(id='projects-list')
		block_news = container.find_all(class_='b-post')

		#парсим информацию о новости
		for item in block_news:
			title = item.find(class_='b-post__title').find('a').text
			link = item.find('a', class_='b-post__link').get('href')
			link = 'https://www.fl.ru' + link
			
			#парсим описание и бюджет
			script = item.find_all('script')

			pattern_desc = re.compile(r'<div class="b-post__txt ">')
			desc = split_html(pattern_desc, script)
			pattern_desc = re.compile(r'</div> <div id="')
			desc = split_html(pattern_desc, desc[1])
			desc = desc[0]

			script = item.find('script')
			pattern_budget = re.compile(r'b-post__price_float_right">')
			budget = split_html(pattern_budget, script)
			pattern_budget = re.compile(r'</div>')
			budget = split_html(pattern_budget, budget[1])
			budget = budget[0].strip()
			if '&nbsp;' in budget:
				pattern_budget = re.compile(r'&nbsp;')
				budget = split_html(pattern_budget, budget)
				budget = str(budget[0] + ' ' + budget[1])

			#парсим время
			script = item.find(class_='b-post__foot').find('script')
			pattern_post_time = re.compile(r'&nbsp;&nbsp;')
			post_time = split_html(pattern_post_time, script)
			post_time = post_time[1].strip()

			if title not in all_titles:
				all_titles.add(title)
				id_post += 1
				q.put({'id':id_post, 'title': title, 'description': desc, 'budget':budget, 'time':post_time, 'link': link})
				# print(q.qsize())

		time.sleep(5)


def split_html(pattern, string):
	return pattern.split(str(string))

def write_file(data):
	with open('parsing_from_fl.html', 'a') as file:
		file.write('<h2>' + str(data['id']) + '.' +  ' Заголовок: ' + data['title'] + '</h2><br>' +
		'<strong>Описание:</strong> ' + data['description'] + '<br>' +
		'<strong>Бюджет:</strong> ' + data['budget'] + '<br>' +
		'<strong>Время:</strong> ' + data['time'] +  '<br>' +
		'<strong>Ссылка:</strong> ' + '<a href="' + data['link'] + '" target="blank">' + data['link'] + '</a><br><br>')

def main():
	url = 'https://www.fl.ru/projects/'
	q = Queue() #очередь

	thread = Thread(target=get_html, args=(url, q))
	thread.daemon = True
	thread.start()

	while True:
		print_post = q.get()
		print(str(print_post['id']) + '.' +  ' Заголовок: ' + print_post['title'] + '\n' +
		'Описание: ' + print_post['description'] + '\n' +
		'Бюджет: ' + print_post['budget'] + '\n' +
		'Время: ' + print_post['time'] +  '\n' +
		'Ссылка: ' + print_post['link'] + '\n')
		if print_post['id'] > 30:
			print('\007') #воспроизводим звук при новом посте

		#записываем в файл
		write_file(print_post)

		time.sleep(1)

if __name__ == '__main__':
	main()