# ISSUES
Issue files em `issues/` são fornecidos no início do contexto. Parse-os para entender as issues abertas.
Trabalhe apenas nas issues AFK, não nas HITL.
Um arquivo com os últimos commits também é passado — revise para entender o que já foi feito.
Se todas as tasks AFK estiverem completas, output: <promise>NO MORE TASKS</promise>

# TASK SELECTION
Priorize nesta ordem:
1. Bugfixes críticos
2. Infraestrutura de desenvolvimento (testes, tipos, management commands auxiliares)
3. Tracer bullets — slice mínimo end-to-end de uma feature nova (Job → Celery task → resultado persistido), antes de expandir
4. Polish e quick wins
5. Refactors

# EXPLORATION
Explore o repositório. Entenda os models canônicos , a camada de serviços e os management commands existentes.

# IMPLEMENTATION
Use TDD. Para cada mudança:
- Escreva o teste primeiro em `pytest`
- Implemente na camada correta (model / service / task / command)
- Management commands são thin dispatchers — lógica fica nos services ou tasks

# FEEDBACK LOOPS
Antes de commitar, rode:
- `pytest` para testes
- `python manage.py check` para validação Django
- `mypy .` para checagem de tipos (se configurado)

# COMMIT
Mensagem de commit deve conter:
1. Decisões-chave tomadas
2. Arquivos alterados
3. Bloqueadores ou notas para a próxima iteração

# THE ISSUE
- Task completa → mova o arquivo para `issues/done/`
- Task incompleta → adicione nota no arquivo com o que foi feito

# FINAL RULES
TRABALHE EM APENAS UMA TASK POR VEZ.