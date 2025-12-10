# utils/after_mixin.py  (novo arquivo)


class AfterManagerMixin:
    """Mixin que registra todos os after() agendados
    e cancela automaticamente no dispose()."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._after_ids: set[str] = set()

    def schedule(self, delay_ms: int, callback, *args, **kwargs):
        aid = self.after(delay_ms, callback, *args, **kwargs)
        self._after_ids.add(aid)
        return aid

    def dispose(self):
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)  # evita callbacks órfãos
            except Exception:
                pass
        self._after_ids.clear()
