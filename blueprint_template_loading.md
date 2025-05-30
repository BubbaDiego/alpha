# Blueprint Template Loading

Flask blueprints in this project define their own `template_folder` so each module can resolve templates relative to its location.  For example `dashboard_bp` sets:

```python
dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='dashboard',
    static_folder='dashboard',
    static_url_path='/dashboard_static'
)
```

When blueprints are registered inside a minimal `Flask` app during tests, the application's template path may not include the repository root.  To ensure shared layouts still render, each blueprint assigns a `ChoiceLoader` that also points at the top‑level `templates/` directory:

```python
ROOT_TEMPLATES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
dashboard_bp.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(os.path.dirname(__file__), 'dashboard')),
    FileSystemLoader(ROOT_TEMPLATES),
])
```

Tests such as `tests/test_dashboard_profit_badge.py` register the blueprint with a bare `Flask` instance:

```python
app = Flask(__name__)
app.register_blueprint(dashboard_bp)
```

Without the `ChoiceLoader`, calls to `render_template` would fail because the project's shared templates would not be found.  The shared templates live in the repository root under `templates/`.

