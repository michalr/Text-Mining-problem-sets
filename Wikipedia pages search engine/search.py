#! /usr/bin/env python
# -*- coding: utf-8 -*-

import database

if __name__ == '__main__':
	stop_words_file = open("stop_words.txt", "rt")
	stop_words_set = set()
	for line in stop_words_file:
		stop_words_set.add(line.rstrip("\r\n").decode('utf-8', 'ignore'))
	stop_words_file.close()
	stop_chars = '.,)(-:/";|?'
	base_forms_file = open("bazy_do_tm.txt", "rt")
	base_forms = {}
	for line in base_forms_file:
		words = line.split()
		words[-1] = words[-1].rstrip("\n")
		base_forms[words[0]] = words[1:]
	base_forms_file.close()
	wiki_titles_file = open("wikipedia_titles_for_tx.txt", "rt")
	wiki_titles_list = []
	for line in wiki_titles_file:
		words = line.split()
		words[-1] = words[-1].rstrip("\n")
		wiki_titles_list.append([float(words[1]), ' '.join(words[2:])])
	while True:
		try:
			query = raw_input(">")
			query_words = filter(lambda word: word not in stop_words_set, query.split())
			query_words_stripped = []
			for word in query_words:
				tmp_word = word.lower().strip(stop_chars)
				if tmp_word:
					query_words_stripped.append(tmp_word)
			cursor = database.get_cursor(None, 'wikipedia.sqlite')
			found = 0
			def doc_cmp(doc1, doc2):
				return cmp(wiki_titles_list[doc1][0], wiki_titles_list[doc2][0])
			try: 
				query_words_title_posting_lists = [set(database.decode_posting_list(database.get_word_title_posting_list(cursor, word))) for word in query_words_stripped]
				title_intersection = query_words_title_posting_lists[0]
				for posting_list in query_words_title_posting_lists[1:]:
					title_intersection = title_intersection & posting_list
			except TypeError:
				title_intersection = set()
			try:
				query_words_body_posting_lists = [set(database.decode_posting_list(database.get_word_body_posting_list(cursor, word))) for word in query_words_stripped]
				body_intersection = query_words_body_posting_lists[0]
				for posting_list in query_words_body_posting_lists[1:]:
					body_intersection = body_intersection & posting_list
			except TypeError:
				body_intersection = set()
			res_intersection = title_intersection & body_intersection
			word_sum = title_intersection | body_intersection
			found = len(word_sum)
			res_intersection_sorted_list = sorted(res_intersection, cmp = doc_cmp, reverse = True)
			titles_only = title_intersection - body_intersection
			titles_only_sorted_list = sorted(titles_only, cmp = doc_cmp, reverse = True)
			body_only = body_intersection - title_intersection
			body_only_sorted_list = sorted(body_only, cmp = doc_cmp, reverse = True)
			# base forms
			query_base_forms = [base_forms.get(word, [word]) for word in query_words_stripped]
			query_base_forms_title_posting_lists = []
			try:
				for baseforms in query_base_forms:
					tmp_posting_lists = []
					for word in baseforms:
						try:
							tmp_posting_lists.append(set(database.decode_posting_list(database.get_base_title_posting_list(cursor, word))))
						except TypeError:
							pass
					if not tmp_posting_lists:
						raise TypeError 
					bf_sum = tmp_posting_lists[0]
					for bf in tmp_posting_lists[1:]:
						bf_sum = bf_sum | bf
				query_base_forms_title_posting_lists.append(bf_sum)
				base_title_intersection = query_base_forms_title_posting_lists[0]
				for bf in query_base_forms_title_posting_lists[1:]:
					base_title_intersection = base_title_intersection & bf
			except TypeError:
				base_title_intersection = set()
			query_base_forms_body_posting_lists = []
			try:
				for baseforms in query_base_forms:
					tmp_posting_lists = []
					for word in baseforms:
						try:
							tmp_posting_lists.append(set(database.decode_posting_list(database.get_base_body_posting_list(cursor, word))))
						except TypeError:
							pass 
					if not tmp_posting_lists:
						raise TypeError
					bf_sum = tmp_posting_lists[0]
					for bf in tmp_posting_lists[1:]:
						bf_sum = bf_sum | bf
					query_base_forms_body_posting_lists.append(bf_sum)
				base_body_intersection = query_base_forms_body_posting_lists[0]
				for bf in query_base_forms_body_posting_lists[1:]:
					base_body_intersection = base_body_intersection & bf
			except TypeError:
				base_body_intersection = set()
			base_res_intersection = base_title_intersection & base_body_intersection
			base_res_sum = base_title_intersection | base_body_intersection
			for doc in base_res_sum:
				if not doc in word_sum:
					found += 1
			base_titles_only = base_title_intersection - base_body_intersection
			base_body_only = base_body_intersection - base_title_intersection
			base_res_intersection_sorted_list = sorted(base_res_intersection, cmp = doc_cmp, reverse = True)
			base_titles_only_sorted_list = sorted(base_titles_only, cmp = doc_cmp, reverse = True)
			base_body_only_sorted_list = sorted(base_body_only, cmp = doc_cmp, reverse = True)
			print "QUERY: %s, %d" % (query, found)
			if found:
				for doc in res_intersection_sorted_list:
					print wiki_titles_list[doc][1]
				for doc in titles_only_sorted_list:
					print wiki_titles_list[doc][1]
				for doc in body_only_sorted_list:
					print wiki_titles_list[doc][1]
				for doc in base_res_intersection_sorted_list:
					if not doc in word_sum:
						print wiki_titles_list[doc][1]
				for doc in base_titles_only_sorted_list:
					if not doc in word_sum:
						print wiki_titles_list[doc][1]
				for doc in base_body_only_sorted_list:
					if not doc in word_sum:
						print wiki_titles_list[doc][1]											
		except EOFError:
			break
	
				
