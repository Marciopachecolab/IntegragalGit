from services.cadastros_diversos import RegistryExamEditor

editor = RegistryExamEditor()
exames = editor.load_all_exams()

# Procurar teste integracao
for nome, slug in exames:
    if 'integracao' in nome:
        print(f'Nome: {repr(nome)}, Slug: {repr(slug)}')
