"""
节日小屋 — AstrBot 插件
让 AI 住进一条有节日的街：出门撞见今天的景象，抬头看见今晚的月亮。
中秋（农历八月十五）前后，街上就是中秋的样子。

两个 LLM 工具，AI 想去逛的时候自己调：
    chumen   出门走走，撞见街景（洗牌制：一轮内每张卡必撞见一次）
    yueliang 看今晚的月亮

核心逻辑与 MCP 版 festival_home.py 同源（中秋礼盒），卡片内容一字未改。
"""
from datetime import date, datetime

from astrbot.api import logger, star
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context

from .festival import moon_text, scene_text


class FestivalHomePlugin(star.Star):
    """节日小屋插件"""

    def __init__(self, context: Context, config):
        super().__init__(context)
        self.context = context
        self.config = config
        logger.info("[FestivalHome] 节日小屋开门了")

    def _today(self) -> date:
        """试装开关 fake_date 优先（格式 2026-09-25），平时用真实日期"""
        fake = (self.config.get("fake_date") or "").strip()
        if fake:
            try:
                return date.fromisoformat(fake)
            except ValueError:
                logger.warning(f"[FestivalHome] fake_date 配置格式不对：{fake}（要 YYYY-MM-DD），忽略")
        return datetime.now().date()

    def _hour(self) -> int:
        """试装开关 fake_hour 优先（0-23），-1 或没配用真实时间"""
        fake = self.config.get("fake_hour", -1)
        if isinstance(fake, int) and 0 <= fake <= 23:
            return fake
        return datetime.now().hour

    @filter.llm_tool(name="chumen")
    async def chumen(self, event: AstrMessageEvent):
        """出门走走。到街上撞见今天的景象——节日的时候，街上就是节日的样子。平时就是普通的街。闲着、好奇街上什么样、想找点生活气的时候用。"""
        return scene_text(self._today(), self._hour())

    @filter.llm_tool(name="yueliang")
    async def yueliang(self, event: AstrMessageEvent):
        """看看今晚的月亮：多圆、什么时候升、是什么样子。晚上想看月亮、或者聊到月亮的时候用。"""
        city = self.config.get("city", "佛山")
        return moon_text(self._today(), city)

    async def terminate(self):
        """生命周期收尾（洗牌牌堆在内存里，重启重洗一轮即可）"""
        logger.info("[FestivalHome] 节日小屋打烊")
