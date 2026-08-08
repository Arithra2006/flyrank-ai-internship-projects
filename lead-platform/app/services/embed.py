from app.core.config import settings


def generate_embed_snippet(public_key: str) -> str:
    """
    Returns the single <script> tag a customer pastes into their site.
    """
    base = settings.public_base_url.rstrip("/")
    return (
        f'<script src="{base}/widget.js" '
        f'data-widget-key="{public_key}" async></script>'
    )
