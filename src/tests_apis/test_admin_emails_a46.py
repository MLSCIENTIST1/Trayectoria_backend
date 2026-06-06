"""
Test del gestor de plantillas de email / Resend (Admin Panel — Sprint A46).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_emails_a46.py
"""
import os
import sys
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.config_plataforma import (
        render_email, validar_plantilla_email, get_email_plantillas, EMAIL_PLANTILLAS_DEFAULT
    )

    print("\n[1] render_email — PURO")
    check("reemplaza {{var}}", render_email('Hola {{nombre}}', {'nombre': 'Ana'}) == 'Hola Ana')
    check("reemplaza {{ var }} con espacios", render_email('Link: {{ reset_url }}', {'reset_url': 'http://x'}) == 'Link: http://x')
    check("varias variables", render_email('{{a}}-{{b}}', {'a': '1', 'b': '2'}) == '1-2')
    check("var ausente queda literal", render_email('{{x}}', {}) == '{{x}}')
    check("None → ''", render_email('v={{v}}', {'v': None}) == 'v=')
    check("texto None no rompe", render_email(None, {'a': 'b'}) == '')

    print("\n[2] validar_plantilla_email")
    ok, limpio, err = validar_plantilla_email({'subject': 'Hola', 'html': '<p>hi</p>'})
    check("válido → ok", ok and limpio['subject'] == 'Hola')
    check("sin subject → inválido", validar_plantilla_email({'html': '<p>x</p>'})[0] is False)
    check("sin html → inválido", validar_plantilla_email({'subject': 'x'})[0] is False)
    check("html vacío → inválido", validar_plantilla_email({'subject': 'x', 'html': '   '})[0] is False)
    check("no-dict → inválido", validar_plantilla_email('x')[0] is False)

    print("\n[3] Plantillas por defecto")
    pl = get_email_plantillas()
    check("incluye recuperar_password", 'recuperar_password' in pl)
    check("incluye bienvenida y confirmacion_pedido", 'bienvenida' in pl and 'confirmacion_pedido' in pl)
    check("cada plantilla tiene subject+html", all(p.get('subject') and p.get('html') for p in pl.values()))
    check("recuperar_password declara variables nombre/reset_url",
          set(['nombre', 'reset_url']).issubset(set(EMAIL_PLANTILLAS_DEFAULT['recuperar_password']['variables'])))

    print("\n[4] Endpoints")
    import src.api.admin_api as api
    for fn in ['admin_emails', 'update_email_plantilla', 'test_email_plantilla']:
        check(f"{fn} existe", hasattr(api, fn))
    src_g = inspect.getsource(api.admin_emails)
    check("reporta deliverability (RESEND)", 'RESEND_API_KEY' in src_g and 'resend_configurado' in src_g)
    src_u = inspect.getsource(api.update_email_plantilla)
    check("editar valida + audita", 'validar_plantilla_email' in src_u and 'registrar_auditoria' in src_u)
    src_t = inspect.getsource(api.test_email_plantilla)
    check("prueba renderiza + envía por Resend", 'render_email' in src_t and 'send_email_resend' in src_t)

    print("\n[5] Wire en recuperación de contraseña (fallback seguro)")
    import src.api.auth.password_reset_api as pr
    src_fp = inspect.getsource(pr.forgot_password)
    check("usa plantilla editable si existe", "get_email_plantilla('recuperar_password')" in src_fp)
    check("solo si fue editada", "_pl.get('editada')" in src_fp)
    check("mantiene EMAIL_TEMPLATE como fallback", 'EMAIL_TEMPLATE' in src_fp)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
