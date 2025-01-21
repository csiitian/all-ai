from flask import Blueprint, jsonify, request, render_template
import requests, json, html, re, markdown
from app.utils.leetcode_helper import clean_html, markdown_to_plain_text

leetcode_blueprint = Blueprint('leetcode', __name__, url_prefix='/api/leetcode')

def get_question(title_slug):
  cookie = request.headers.get('Cookie')
  try:
    graphql_query = "query questionDetail($titleSlug: String!) { languageList { id name } submittableLanguageList { id name verboseName } statusList { id name } questionDiscussionTopic(questionSlug: $titleSlug) { id commentCount topLevelCommentCount } ugcArticleOfficialSolutionArticle(questionSlug: $titleSlug) { uuid chargeType canSee hasVideoArticle } question(titleSlug: $titleSlug) { title titleSlug questionId questionFrontendId questionTitle translatedTitle content translatedContent categoryTitle difficulty topicTags { name slug translatedName } similarQuestionList { difficulty titleSlug title translatedTitle isPaidOnly } stats companyTagStatsV2 mysqlSchemas dataSchemas frontendPreviews likes dislikes isPaidOnly status canSeeQuestion enableTestMode enableRunCode enableSubmit enableDebugger envInfo isLiked nextChallenges { difficulty title titleSlug questionFrontendId } libraryUrl adminUrl hints codeSnippets { code lang langSlug } exampleTestcaseList hasFrontendPreview } }"
    response = requests.post(
      "https://leetcode.com/graphql",
      json={"query": graphql_query, "variables": {"titleSlug": title_slug}},
      headers={
        'Content-Type': 'application/json',
        'Cookie': cookie
      }
    )
    print(response)
    data = response.json()
    print(data)
    question = data['data']['question']
    return question
  except Exception as e:
    return jsonify({'error': str(e)})

@leetcode_blueprint.route("/solution/<string:topicId>")
def get_leetcode_solution(topicId):
  cookie = request.headers.get('Cookie')
  try:
    graphql_query = "query ugcArticleSolutionArticle($articleId: ID, $topicId: ID) { ugcArticleSolutionArticle(articleId: $articleId, topicId: $topicId) { content title author { userName realName userSlug } createdAt updatedAt hitCount reactions { count reactionType } } }"
    response = requests.get(
      "https://leetcode.com/graphql",
      json={
          "operationName": "ugcArticleSolutionArticle",
          "variables": {"topicId": topicId},
          "query": graphql_query
      },
      headers={
          'Content-Type': 'application/json',
          'Cookie': cookie
      }
    )
    data = response.json()
    result = data['data']['ugcArticleSolutionArticle']
    return result
  except Exception as e:
    return jsonify({'error': str(e)})

@leetcode_blueprint.route("/daily-challenge")
def fetch_daily_coding_challenge():
  cookie = request.headers.get('Cookie')
  try:
    graphql_query = "query questionOfToday { activeDailyCodingChallengeQuestion { date userStatus link question { acRate difficulty freqBar frontendQuestionId: questionFrontendId isFavor status title titleSlug hasVideoSolution hasSolution topicTags { name id slug } } } }"
    response = requests.post(
      "https://leetcode.com/graphql",
      json={"query": graphql_query},
      headers={
        'Content-Type': 'application/json',
        'Cookie': cookie
      }
    )
    data = response.json()
    title_slug = data['data']['activeDailyCodingChallengeQuestion']['question']['titleSlug']
    return get_question(title_slug)
  except Exception as e:
    return jsonify({'error': str(e)})

@leetcode_blueprint.route("/questions")
def fetch_all_questions():
  query = "query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) { problemsetQuestionList: questionList(categorySlug: $categorySlug, limit: $limit, skip: $skip, filters: $filters) { total: totalNum questions: data { acRate difficulty freqBar frontendQuestionId: questionFrontendId isFavor paidOnly: isPaidOnly status title titleSlug topicTags { name id slug } hasSolution hasVideoSolution } } }"
  page = (int)(request.args.get('page', 1))
  limit = (int)(request.args.get('limit', 10))
  filters = request.args.get('filters', '{}')  # Default to '{}' as a string

  variables = {
    "categorySlug": "all-code-essentials",
    "skip": (page - 1) * limit,
    "limit": limit,
    "filters": {}
  }

  try:
    filters_dict = json.loads(filters) if isinstance(filters, str) else {}
    if isinstance(filters_dict, dict) and filters_dict:
      variables["filters"] = filters_dict
  except json.JSONDecodeError:
    pass

  try:
    response = requests.get(
      'https://leetcode.com/graphql/',
      json = {
        "query": query,
        "variables": variables,
        "operationName": "problemsetQuestionList"
      },
      headers={
        "Content-Type":"application/json",
        "cookie": "_ga=GA1.2.711721837.1646152226; gr_user_id=dfcf9a50-9bf9-47e3-b7d4-a0a8b0bae903; csrftoken=IkY58XGXE0JiufOuTivuTKOrTRo9LqlEky8rU8CSp3nrQuJc37nMlHP7jbAFKp74; __stripe_mid=be6845bb-3b2a-420f-9609-158604c82ad6655d69; 87b5a3c3f1a55520_gr_last_sent_cs1=Vikasss_7663; NEW_PROBLEMLIST_PAGE=1; _gid=GA1.2.501643573.1651371365; __atuvc=0|14,1|15,1|16,0|17,4|18; c_a_u=VmlrYXNzc183NjYz:1nl1D7:JMV_egBn6_ra6aM4BQxrSmFTEkQ; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzYzMzYwMCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImFsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImU3ZjM0MmM5MTA0MDYxZDk3NTQwNjRkMTJkNDFlNWZmZjEwNmFhNGQiLCJpZCI6MzYzMzYwMCwiZW1haWwiOiJ2aXNoYWxzaW5naGdrMjAxOEBnbWFpbC5jb20iLCJ1c2VybmFtZSI6IlZpa2Fzc3NfNzY2MyIsInVzZXJfc2x1ZyI6IlZpa2Fzc3NfNzY2MyIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9pZDY5NDcvYXZhdGFyXzE2MTQzMzEwOTkucG5nIiwicmVmcmVzaGVkX2F0IjoxNjUxMzc5NDA1LCJpcCI6IjI0MDE6NDkwMDo1YmEzOjcxZjc6NDQzZToyMmVlOjcwYTU6NDc4NiIsImlkZW50aXR5IjoiZGM2YjUzZGFjNmI5YTVlNzA0YTZhNzUxYjk1N2EyOGQiLCJzZXNzaW9uX2lkIjoxODYzMzE4Nn0.m1DiL8xoMyE-WQ886xIsFiRvzNQQQvxSCICmpS4opT0; 87b5a3c3f1a55520_gr_session_id=e44ac732-b14d-4b32-81f4-0d243dbf68ea; 87b5a3c3f1a55520_gr_last_sent_sid_with_cs1=e44ac732-b14d-4b32-81f4-0d243dbf68ea; 87b5a3c3f1a55520_gr_session_id_e44ac732-b14d-4b32-81f4-0d243dbf68ea=true; 87b5a3c3f1a55520_gr_cs1=Vikasss_7663; _gat=1"
      }
    )
    result = response.json()['data']['problemsetQuestionList']['questions']
    return result
  except Exception as e:
    return jsonify({'error': str(e)})

@leetcode_blueprint.route("/save-question-and-solution")
def save_question_and_solution():
  title_slug_map = {
    "palindromic-substrings": 4703811,
    "palindrome-linked-list": 4908031,
    "cherry-pickup-ii": 4708405,
    "furthest-building-you-can-reach": 4739509,
    "find-the-duplicate-number": 4916443,
    "minimum-height-trees": 5060930,
    "rearrange-array-elements-by-sign": 4723827,
    "delete-leaves-with-a-given-value": 5167692,
    "largest-divisible-subset": 4699839,
    "distribute-coins-in-binary-tree": 5172479,
    "majority-element": 4713244,
    "perfect-squares": 4694964,
    "find-the-safest-path-in-a-grid": 5158865,
    "reorder-list": 4250201,
    "reverse-linked-list": 4904297
  }
  for title_slug, topicId in title_slug_map.items():
    print(f"Fetching question and solution for {title_slug}", topicId)
    question = get_question(title_slug=title_slug)['content']
    solution = get_leetcode_solution(topicId)
    prompt = clean_html(question)
    completion = markdown_to_plain_text(solution)
    with open(f"static/fine_tune/leetcode_solution.jsonl", "a") as f:
      json.dump({"prompt": prompt, "completion": completion}, f)
      f.write(",\n")
  return jsonify({"message": "Question and solution saved successfully"})
