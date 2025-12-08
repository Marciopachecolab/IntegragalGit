def dump_df(tag, df, extra=None, head=5):
    try:
        print(f"[DFDBG] {tag}: shape={df.shape} cols={list(df.columns)}")
        if extra:
            print(f"[DFDBG] {tag} extra={extra}")
        print(df.head(head))
    except Exception as e:
        print(f"[DFDBG] {tag} erro ao inspecionar DF: {e}")
