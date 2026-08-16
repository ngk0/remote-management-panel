from pitft_oob.models import Health
from pitft_oob.ui.viewmodels import RowView


def build_menu_rows() -> tuple[RowView, ...]:
    """Stable status-navigation routes; privileged controls are not exposed."""
    return (
        RowView("Overview", "STATUS", Health.OK, "home"),
        RowView("Cloudflare", "DETAIL", Health.OK, "cloudflared"),
        RowView("Network", "DETAIL", Health.OK, "network"),
        RowView("System", "DETAIL", Health.OK, "system"),
        RowView("Services", "DETAIL", Health.OK, "services"),
    )
