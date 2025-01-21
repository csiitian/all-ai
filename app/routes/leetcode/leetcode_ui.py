from flask import Blueprint, jsonify, request, render_template
import requests, json, html, re, markdown
from app.utils.leetcode_helper import clean_html, markdown_to_plain_text
from .leetcode import get_question, fetch_all_questions
import markdown
from markupsafe import Markup

leetcode_ui_blueprint = Blueprint('leetcode_ui', __name__, url_prefix='/leetcode')

@leetcode_ui_blueprint.route("/question/<string:title_slug>")
def get_question_content(title_slug):
  try:
    question = get_question(title_slug=title_slug)
    print(question['content'])
    return render_template("leetcode_question.html", 
      question = question['content'], 
      question_title = question['title'],
      question_id = question['questionFrontendId'], 
      difficulty = question['difficulty'],
      topic_tags = question['topicTags'])
  except Exception as e:
    return jsonify({'error': str(e)})

@leetcode_ui_blueprint.route("/")
def get_home_page():
  questions = fetch_all_questions()
  return render_template("leetcode_home.html", questions=questions)

@leetcode_ui_blueprint.route("/solution/<string:titleSlug>")
def get_leetcode_solution(titleSlug):
    cookie = request.headers.get('Cookie')
    try:
      graphql_query = """query ugcArticleOfficialSolutionArticle($questionSlug: String!) { ugcArticleOfficialSolutionArticle(questionSlug: $questionSlug) { uuid title slug content createdAt author { realName userAvatar userName } } }"""
      response = requests.post(
        "https://leetcode.com/graphql/",
        json={"query": graphql_query, "variables": {"questionSlug": titleSlug}, "operationName": "ugcArticleOfficialSolutionArticle"},
        headers={
          'Content-Type': 'application/json',
          'Cookie': cookie
        }
      )
      data = response.json()
      solution = data['data']['ugcArticleOfficialSolutionArticle']

      return render_template(
        'leetcode_solution.html',
        title=solution['title'],
        author=solution['author'],
        createdAt=solution['createdAt'],
        content=solution['content']
      )
    except Exception as e:
      return jsonify({'error': str(e)}), 500
