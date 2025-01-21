from .leetcode.leetcode import leetcode_blueprint
from .open_ai import open_ai_text_blueprint, open_ai_image_blueprint, open_ai_audio_blueprint
from .leetcode.leetcode_ui import leetcode_ui_blueprint

def register_routes(app):
  app.register_blueprint(leetcode_blueprint)
  app.register_blueprint(leetcode_ui_blueprint)
  app.register_blueprint(open_ai_text_blueprint)
  app.register_blueprint(open_ai_image_blueprint)
  app.register_blueprint(open_ai_audio_blueprint)