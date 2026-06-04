# 📚 INVENTARIO DE DOCUMENTACIÓN — TuKomercio

> Inventario para compartir contexto con otro asistente. Generado: 2026-06-04.
> Cubre dos ubicaciones: la **memoria de Claude** (roadmaps/contexto vivos) y la carpeta **SENA_TuKomercio_2026** (plan de negocio formal SENA).

---

## 1. Carpeta `memory/`
`C:\Users\carlo\.claude\projects\C--Users-carlo-Desktop\memory\`
> Memoria interna de Claude (no es parte de los repos de código). Es la "fuente de verdad" del seguimiento.

| Documento | Descripción | Estado |
|---|---|---|
| `MEMORY.md` | Índice maestro de la memoria: enlaza todos los demás documentos con una línea de resumen cada uno. Punto de entrada. | 🟢 Vigente |
| `user_carlos.md` | Perfil del usuario/dueño: Carlos, desarrollador Flask + Vanilla JS en Bogotá, único dev del proyecto. Define rol y nivel técnico. | 🟢 Vigente |
| `project_tukomercio.md` | Contexto del proyecto: qué es TuKomercio (SaaS e-commerce multi-tenant para tenderos), stack, rutas de las carpetas físicas y pendientes históricos. | 🟢 Vigente (algún pendiente ya resuelto) |
| `feedback_tukomercio_convenciones.md` | Convenciones de código obligatorias: sin frameworks JS, modales con `.show`/`.active`, no inventar endpoints, leer antes de modificar. | 🟢 Vigente |
| `feedback_repos_structure.md` | ⚠️ Regla CRÍTICA: dos repos separados (Backend = `trayectoria 30 dic/`, Frontend = `proyecto_sena/.../public/`). Nunca mezclarlos. | 🟢 Vigente |
| `gamification_roadmap.md` | Roadmap de los 40 sprints de gamificación (S1–S40): XP, niveles, misiones, TuKoins, insignias, ligas, duelos, eventos, etc. Con commits y notas por sprint. | ✅ Completado (40/40, 346 tests) |
| `admin_panel_roadmap.md` | Roadmap de los 49 sprints del Panel de Administración (A1–A49, 6 fases). Meta: administrar todo sin tocar código. Incluye auditoría del panel actual. | 🟡 En curso (10/49; Fase 0 ✅, Fase 1 5/9) |
| `fixes_tienda_checkout.md` | Bugs de producción de tienda/checkout (F1–F3): resumen de pedido sin color/logo de la tienda + inconsistencia del valor de envío. Con diagnóstico de causa raíz. | 🟡 Vigente — pendiente (0/3) |

---

## 2. Carpeta `SENA_TuKomercio_2026/`
`C:\Users\carlo\Desktop\SENA_TuKomercio_2026\`
> Plan de negocio formal para el SENA (formato GFPI-F-144) + soportes de marketing y legales. Documentación de negocio, **no** de código.

### 📄 Índice
| Archivo | Qué es / para qué sirve |
|---|---|
| `LEEME.md` | Índice maestro de esta carpeta: inventario, qué contiene cada doc, las 3 observaciones del SENA y los archivos `_v2` corregidos. **Empezar por aquí.** |

### 🟦 Plan de negocio SENA (formato GFPI-F-144) — versiones originales y `_v2` (corregidas)
| Archivo | Qué es / para qué sirve |
|---|---|
| `GFPI-F-144_Seccion1_Generalidades_TuKomercio.docx` | Sección 1: generalidades — problema, objetivos, justificación del proyecto. |
| `GFPI-F-144_Seccion2_EstudioMercados_TuKomercio.docx` (+ `_v2`) | Sección 2: estudio de mercados (oferta, demanda, segmentación, competencia). |
| `GFPI-F-144_Seccion2_Complemento_TuKomercio.docx` (+ `_v2`) | Anexo complementario al estudio de mercados. |
| `GFPI-F-144_Seccion3_EstudioTecnico_TuKomercio.docx` (+ `_v2`) | Sección 3: estudio técnico (arquitectura, requerimientos, infraestructura). |
| `GFPI-F-144_Seccion4_Organizacional_TuKomercio.docx` | Sección 4: estructura organizacional, roles y perfiles. |
| `GFPI-F-144_Seccion5_Financiero_TuKomercio.docx` (+ `_v2`) | Sección 5: plan financiero, costos y proyecciones. |

### 🟩 Anexos del plan
| Archivo | Qué es / para qué sirve |
|---|---|
| `Anexo_ResumenEjecutivo_MapaProcesos_TuKomercio.docx` (+ `_v2`) | Resumen ejecutivo + mapa de procesos del negocio. |
| `Anexo_CalidadSoftware_TuKomercio.docx` (+ `_v2`) | Plan de calidad de software. |
| `Anexo_Manuales_TuKomercio.docx` | Manuales de usuario y técnico. |
| `Guia_Sustentacion_TuKomercio.docx` | Guía para la sustentación oral ante el SENA. |

### 🟨 Correcciones SENA (Markdown de trabajo)
| Archivo | Qué es / para qué sirve |
|---|---|
| `OBSERVACIONES_SENA_v2.md` | Consolidado de las observaciones del SENA y las correcciones a aplicar. |
| `Correcciones_Seccion2_EstudioMercados_v2.md` | Texto corregido de la Sección 2 (mercados) para volcar al .docx. |
| `Correcciones_Seccion3_AnaliticaIntegraciones_v2.md` | Correcciones de analítica/integraciones (Sección 3). |
| `Correcciones_Seccion3_EstudioTecnico_v2.md` | Correcciones del estudio técnico (Sección 3). |
| `Correcciones_Seccion5_Financiero_Roadmap_v2.md` | Correcciones del financiero + roadmap (Sección 5). |
| `Diagrama_Arquitectura_v2.md` | Diagrama de arquitectura (ASCII/Mermaid) para insertar en la Sección 3.1. |
| `aplicar_correcciones.py` | Script Python que aplica las correcciones a los .docx (genera las versiones `_v2`). |

### 🟧 Marketing y lanzamiento
| Archivo | Qué es / para qué sirve |
|---|---|
| `campana_publicitaria_tukomercio.md` | Análisis de público objetivo + campaña publicitaria. |
| `plan_lanzamiento_tukomercio.md` | Plan de lanzamiento (feb 9–28, 2026; meta: 5 negocios registrados). |
| `tukomercio-brief-produccion.docx` | Brief de producción (audiovisual/publicitario). |
| `notas_por_mejorar_mas_ventas_menos_codigo.txt` | Notas estratégicas: enfoque en ventas/tracción antes que más código (primer contratado = vendedor). |

### 🟥 Roadmap de gamificación (versión documento de negocio)
| Archivo | Qué es / para qué sirve |
|---|---|
| `TUKOMERCIO_GAMIFICACION_ROADMAP_v1_2.md` | Documento de diseño de gamificación v1.2 (ene 2026): BizScore, badges, niveles. **Predecesor** del roadmap de implementación; histórico. |

### ⚖️ Legales y reconocimientos
| Archivo | Qué es / para qué sirve |
|---|---|
| `DECLARACIÓN JURADA DE AUTORÍA Y TITULARIDAD 04022026.docx` | Declaración jurada de autoría/titularidad (borrador, 04-02-2026). |
| `DECLARACIÓN JURADA DE AUTORÍA Y TITULARIDAD firmado.docx` / `.pdf` | Versión firmada de la declaración jurada (DOCX + PDF). |
| `diploma-modelos-negocio.pdf` | Diploma/certificado de modelos de negocio (soporte de formación). |

### 🗂️ Otros / trabajo en curso
| Archivo | Qué es / para qué sirve |
|---|---|
| `Por solucionar.docx` | Lista de pendientes por resolver del plan SENA. |
| `recuperado rodar plant.docx` | Documento recuperado relacionado con la tienda demo "Rodar" (plantilla/contenido). |

---

> **Nota:** los archivos con sufijo `_v2` son las versiones **corregidas** tras las observaciones del SENA;
> conviven con los originales. La documentación de **código** (no incluida aquí) está en
> `CLAUDE.md`, `BITACORA.md` (raíz del repo backend) y `TuKomercio_Funcionalidades.md` (escritorio).
