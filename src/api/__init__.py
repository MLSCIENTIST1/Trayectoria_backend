<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carga Masiva CSV - BizFlow</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #e0e7ff;
            --success: #10b981;
            --success-light: #d1fae5;
            --danger: #ef4444;
            --danger-light: #fee2e2;
            --warning: #f59e0b;
            --warning-light: #fef3c7;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            --radius: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--gray-100);
            color: var(--gray-800);
            min-height: 100vh;
            padding: 24px;
            background-image: 
                radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                radial-gradient(at 0% 100%, rgba(139, 92, 246, 0.08) 0px, transparent 50%);
        }

        .csv-container { max-width: 1100px; margin: 0 auto; }

        /* Header */
        .page-header {
            background: var(--gradient-primary);
            border-radius: var(--radius-xl);
            padding: 32px 40px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-lg);
        }

        .page-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -30%;
            width: 100%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        }

        .header-content {
            position: relative;
            z-index: 1;
            color: white;
        }

        .header-content h1 {
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .header-content p { opacity: 0.9; font-size: 0.95rem; }

        /* Upload Area */
        .upload-section {
            background: white;
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--shadow);
        }

        .upload-area {
            border: 3px dashed var(--gray-300);
            border-radius: var(--radius-lg);
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--gray-50);
        }

        .upload-area:hover {
            border-color: var(--primary);
            background: var(--primary-light);
        }

        .upload-area.dragover {
            border-color: var(--primary);
            background: var(--primary-light);
            transform: scale(1.01);
        }

        .upload-area i {
            font-size: 4rem;
            color: var(--primary);
            margin-bottom: 16px;
            display: block;
        }

        .upload-area h3 {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 8px;
        }

        .upload-area p {
            color: var(--gray-500);
            font-size: 0.9rem;
        }

        /* Required Fields Info */
        .fields-info {
            margin-top: 20px;
            padding: 16px 20px;
            background: var(--warning-light);
            border-radius: var(--radius);
            border-left: 4px solid var(--warning);
        }

        .fields-info h4 {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--warning);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .fields-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 8px;
        }

        .field-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: white;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .field-tag.required { color: var(--danger); }
        .field-tag.optional { color: var(--gray-600); }

        /* Preview Section */
        .preview-section {
            background: white;
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--shadow);
            display: none;
        }

        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--gray-100);
        }

        .preview-header h3 {
            font-size: 1.1rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .preview-header h3 i { color: var(--primary); }

        .preview-stats {
            display: flex;
            gap: 16px;
        }

        .stat-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .stat-badge.success { background: var(--success-light); color: var(--success); }
        .stat-badge.warning { background: var(--warning-light); color: var(--warning); }
        .stat-badge.error { background: var(--danger-light); color: var(--danger); }

        /* Validation Messages */
        .validation-box {
            padding: 16px;
            border-radius: var(--radius);
            margin-bottom: 16px;
            display: none;
        }

        .validation-box.error {
            background: var(--danger-light);
            border: 1px solid var(--danger);
            color: var(--danger);
            display: block;
        }

        .validation-box.success {
            background: var(--success-light);
            border: 1px solid var(--success);
            color: var(--success);
            display: block;
        }

        .validation-box ul {
            margin: 8px 0 0 20px;
            font-size: 0.85rem;
        }

        /* Table */
        .table-container {
            overflow-x: auto;
            border-radius: var(--radius);
            border: 1px solid var(--gray-200);
        }

        .preview-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        .preview-table th {
            background: var(--gray-100);
            padding: 14px 16px;
            text-align: left;
            font-weight: 700;
            color: var(--gray-700);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--gray-200);
            white-space: nowrap;
        }

        .preview-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--gray-100);
            color: var(--gray-700);
        }

        .preview-table tr:hover { background: var(--gray-50); }

        .preview-table .row-number {
            color: var(--gray-400);
            font-weight: 600;
            width: 50px;
        }

        .preview-table .cell-error {
            background: var(--danger-light);
            color: var(--danger);
            font-weight: 600;
        }

        .more-rows {
            text-align: center;
            padding: 16px;
            color: var(--gray-500);
            font-style: italic;
        }

        /* Progress */
        .progress-section {
            margin-top: 20px;
            display: none;
        }

        .progress-bar-container {
            height: 12px;
            background: var(--gray-200);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 12px;
        }

        .progress-bar {
            height: 100%;
            background: var(--gradient-primary);
            border-radius: 10px;
            transition: width 0.3s;
            width: 0%;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--gray-600);
        }

        /* Buttons */
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: var(--radius);
            font-size: 0.95rem;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: all 0.2s;
        }

        .btn-primary {
            background: var(--gradient-primary);
            color: white;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        }

        .btn-primary:disabled {
            background: var(--gray-300);
            cursor: not-allowed;
            box-shadow: none;
        }

        .btn-secondary {
            background: var(--gray-200);
            color: var(--gray-700);
        }

        .btn-secondary:hover { background: var(--gray-300); }

        .btn-danger {
            background: var(--danger);
            color: white;
        }

        .action-buttons {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        /* Results */
        .results-section {
            background: white;
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow);
            display: none;
        }

        .result-summary {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .result-card {
            padding: 20px;
            border-radius: var(--radius);
            text-align: center;
        }

        .result-card.success { background: var(--success-light); }
        .result-card.error { background: var(--danger-light); }
        .result-card.total { background: var(--gray-100); }

        .result-card .number {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .result-card.success .number { color: var(--success); }
        .result-card.error .number { color: var(--danger); }
        .result-card.total .number { color: var(--gray-700); }

        .result-card .label {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--gray-600);
        }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: var(--gray-800);
            color: white;
            padding: 16px 24px;
            border-radius: var(--radius);
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            opacity: 0;
            transition: all 0.3s;
        }

        .toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
        .toast.success { background: var(--success); }
        .toast.error { background: var(--danger); }

        /* Loading spinner */
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* Responsive */
        @media (max-width: 768px) {
            body { padding: 16px; }
            .page-header { padding: 24px; }
            .upload-area { padding: 40px 20px; }
            .fields-grid { grid-template-columns: 1fr 1fr; }
            .result-summary { grid-template-columns: 1fr; }
            .action-buttons { flex-direction: column; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="csv-container">
        <!-- Header -->
        <header class="page-header">
            <div class="header-content">
                <h1><i class="bi bi-file-earmark-spreadsheet"></i> Carga Masiva de Inventario</h1>
                <p>Importa tu catálogo de productos desde un archivo CSV en segundos</p>
            </div>
        </header>

        <!-- Upload Section -->
        <div class="upload-section">
            <div class="upload-area" id="dropZone">
                <i class="bi bi-cloud-arrow-up"></i>
                <h3>Arrastra tu archivo CSV aquí</h3>
                <p>o haz clic para seleccionar desde tu dispositivo</p>
                <input type="file" id="fileInput" accept=".csv" style="display:none;">
            </div>

            <div class="fields-info">
                <h4><i class="bi bi-info-circle"></i> Columnas del CSV</h4>
                <div class="fields-grid">
                    <span class="field-tag required">● nombre *</span>
                    <span class="field-tag required">● precio *</span>
                    <span class="field-tag required">● stock *</span>
                    <span class="field-tag optional">○ costo</span>
                    <span class="field-tag optional">○ sku</span>
                    <span class="field-tag optional">○ categoria</span>
                    <span class="field-tag optional">○ descripcion</span>
                </div>
            </div>
        </div>

        <!-- Preview Section -->
        <div class="preview-section" id="previewSection">
            <div class="preview-header">
                <h3><i class="bi bi-table"></i> Vista Previa</h3>
                <div class="preview-stats">
                    <span class="stat-badge success" id="validCount">0 válidos</span>
                    <span class="stat-badge error" id="errorCount" style="display:none;">0 errores</span>
                </div>
            </div>

            <div class="validation-box" id="validationBox"></div>

            <div class="table-container">
                <table class="preview-table">
                    <thead id="previewThead"></thead>
                    <tbody id="previewTbody"></tbody>
                </table>
            </div>

            <div class="progress-section" id="progressSection">
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="progress-text">
                    <span id="progressText">Preparando carga...</span>
                    <span id="progressPercent">0%</span>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="resetUpload()">
                    <i class="bi bi-arrow-counterclockwise"></i> Cancelar
                </button>
                <button class="btn btn-primary" id="btnUpload" onclick="startUpload()">
                    <i class="bi bi-cloud-upload"></i> Cargar al Inventario
                </button>
            </div>
        </div>

        <!-- Results Section -->
        <div class="results-section" id="resultsSection">
            <h3 style="margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <i class="bi bi-check-circle" style="color: var(--success);"></i> Carga Completada
            </h3>
            
            <div class="result-summary">
                <div class="result-card total">
                    <div class="number" id="resultTotal">0</div>
                    <div class="label">Total Procesados</div>
                </div>
                <div class="result-card success">
                    <div class="number" id="resultSuccess">0</div>
                    <div class="label">Cargados Exitosamente</div>
                </div>
                <div class="result-card error">
                    <div class="number" id="resultErrors">0</div>
                    <div class="label">Con Errores</div>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="resetUpload()">
                    <i class="bi bi-plus-lg"></i> Cargar Otro Archivo
                </button>
                <button class="btn btn-primary" onclick="goToInventory()">
                    <i class="bi bi-box-seam"></i> Ver Inventario
                </button>
            </div>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast"></div>

    <script>
        // ==========================================
        // CONFIGURACIÓN
        // ==========================================
        const API_URL = window.APP_CONFIG?.API_BASE_URL || 'https://trayectoria-backend.onrender.com/api';
        const userId = localStorage.getItem('usuario_id') || '0';
        const businessId = localStorage.getItem('negocio_id') || localStorage.getItem('active_business_id') || '0';
        const branchId = localStorage.getItem('sucursal_id') || '1';

        // Campos requeridos y opcionales
        const REQUIRED_FIELDS = ['nombre', 'precio', 'stock'];
        const OPTIONAL_FIELDS = ['costo', 'sku', 'categoria', 'descripcion', 'referencia_sku', 'codigo_barras'];
        
        // Mapeo de nombres alternativos de columnas
        const FIELD_ALIASES = {
            'nombre': ['nombre', 'name', 'producto', 'product', 'articulo'],
            'precio': ['precio', 'price', 'valor', 'precio_venta'],
            'stock': ['stock', 'cantidad', 'qty', 'quantity', 'inventario'],
            'costo': ['costo', 'cost', 'precio_compra', 'costo_unitario'],
            'sku': ['sku', 'codigo', 'code', 'referencia', 'referencia_sku', 'ref'],
            'categoria': ['categoria', 'category', 'tipo', 'type'],
            'descripcion': ['descripcion', 'description', 'detalle', 'desc']
        };

        let rawData = [];
        let validatedData = [];
        let columnMapping = {};

        // ==========================================
        // INICIALIZACIÓN
        // ==========================================
        document.addEventListener('DOMContentLoaded', () => {
            if (businessId === '0') {
                showToast('⚠️ Selecciona un negocio primero', 'error');
            }

            setupDragAndDrop();
            setupFileInput();
        });

        function setupDragAndDrop() {
            const dropZone = document.getElementById('dropZone');

            dropZone.addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });

            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragover');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                
                const file = e.dataTransfer.files[0];
                if (file && file.name.endsWith('.csv')) {
                    processFile(file);
                } else {
                    showToast('Por favor selecciona un archivo CSV', 'error');
                }
            });
        }

        function setupFileInput() {
            document.getElementById('fileInput').addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    processFile(file);
                }
            });
        }

        // ==========================================
        // PROCESAMIENTO DEL CSV
        // ==========================================
        function processFile(file) {
            const reader = new FileReader();
            reader.onload = (e) => parseCSV(e.target.result);
            reader.onerror = () => showToast('Error al leer el archivo', 'error');
            reader.readAsText(file, 'UTF-8');
        }

        function parseCSV(text) {
            // Detectar separador (coma o punto y coma)
            const firstLine = text.split('\n')[0];
            const separator = firstLine.includes(';') ? ';' : ',';
            
            const lines = text.split('\n').filter(line => line.trim() !== '');
            
            if (lines.length < 2) {
                showToast('El archivo está vacío o solo tiene encabezados', 'error');
                return;
            }

            // Parsear headers
            const headers = lines[0].split(separator).map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
            console.log('📋 Columnas detectadas:', headers);

            // Mapear columnas
            columnMapping = mapColumns(headers);
            console.log('🔗 Mapeo de columnas:', columnMapping);

            // Validar que existan las columnas requeridas
            const missingRequired = REQUIRED_FIELDS.filter(field => !columnMapping[field] && columnMapping[field] !== 0);
            
            if (missingRequired.length > 0) {
                showValidationError(`Faltan columnas requeridas: ${missingRequired.join(', ')}`);
                return;
            }

            // Parsear datos
            rawData = [];
            for (let i = 1; i < lines.length; i++) {
                const values = parseCSVLine(lines[i], separator);
                if (values.length === 0) continue;

                const row = {};
                headers.forEach((header, idx) => {
                    row[header] = values[idx]?.trim() || '';
                });
                rawData.push(row);
            }

            // Validar y transformar datos
            validateData();
            
            // Mostrar preview
            showPreview(headers);
        }

        function parseCSVLine(line, separator) {
            // Manejo básico de comillas en CSV
            const result = [];
            let current = '';
            let inQuotes = false;

            for (let char of line) {
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === separator && !inQuotes) {
                    result.push(current);
                    current = '';
                } else {
                    current += char;
                }
            }
            result.push(current);
            return result;
        }

        function mapColumns(headers) {
            const mapping = {};
            
            for (const [field, aliases] of Object.entries(FIELD_ALIASES)) {
                const foundIndex = headers.findIndex(h => aliases.includes(h));
                if (foundIndex !== -1) {
                    mapping[field] = headers[foundIndex];
                }
            }
            
            return mapping;
        }

        function validateData() {
            validatedData = [];
            let errors = [];

            rawData.forEach((row, index) => {
                const rowErrors = [];
                const validRow = {};

                // Validar nombre
                const nombre = row[columnMapping.nombre];
                if (!nombre || nombre.trim() === '') {
                    rowErrors.push('nombre vacío');
                } else {
                    validRow.nombre = nombre.trim();
                }

                // Validar precio
                const precio = parseFloat(row[columnMapping.precio]?.replace(/[,$]/g, ''));
                if (isNaN(precio) || precio < 0) {
                    rowErrors.push('precio inválido');
                } else {
                    validRow.precio = precio;
                }

                // Validar stock
                const stock = parseInt(row[columnMapping.stock]);
                if (isNaN(stock) || stock < 0) {
                    rowErrors.push('stock inválido');
                } else {
                    validRow.stock = stock;
                }

                // Campos opcionales
                if (columnMapping.costo) {
                    const costo = parseFloat(row[columnMapping.costo]?.replace(/[,$]/g, ''));
                    validRow.costo = isNaN(costo) ? 0 : costo;
                }

                if (columnMapping.sku) {
                    validRow.referencia_sku = row[columnMapping.sku]?.trim() || '';
                }

                if (columnMapping.categoria) {
                    validRow.categoria = row[columnMapping.categoria]?.trim() || 'General';
                }

                if (columnMapping.descripcion) {
                    validRow.descripcion = row[columnMapping.descripcion]?.trim() || '';
                }

                // Agregar metadata
                validRow._rowIndex = index + 2; // +2 porque fila 1 es header
                validRow._errors = rowErrors;
                validRow._valid = rowErrors.length === 0;

                validatedData.push(validRow);
            });

            const validCount = validatedData.filter(r => r._valid).length;
            const errorCount = validatedData.filter(r => !r._valid).length;

            console.log(`✅ Validación: ${validCount} válidos, ${errorCount} con errores`);
        }

        // ==========================================
        // MOSTRAR PREVIEW
        // ==========================================
        function showPreview(headers) {
            const previewSection = document.getElementById('previewSection');
            const thead = document.getElementById('previewThead');
            const tbody = document.getElementById('previewTbody');

            // Stats
            const validCount = validatedData.filter(r => r._valid).length;
            const errorCount = validatedData.filter(r => !r._valid).length;

            document.getElementById('validCount').textContent = `${validCount} válidos`;
            
            const errorBadge = document.getElementById('errorCount');
            if (errorCount > 0) {
                errorBadge.style.display = 'inline-block';
                errorBadge.textContent = `${errorCount} errores`;
            } else {
                errorBadge.style.display = 'none';
            }

            // Validation message
            if (errorCount > 0) {
                showValidationError(`${errorCount} filas tienen errores y no serán cargadas`);
            } else {
                showValidationSuccess(`${validCount} productos listos para cargar`);
            }

            // Table headers
            const mappedHeaders = ['#', 'Nombre', 'Precio', 'Stock', 'Costo', 'SKU', 'Categoría'];
            thead.innerHTML = `<tr>${mappedHeaders.map(h => `<th>${h}</th>`).join('')}</tr>`;

            // Table body (mostrar primeras 10 filas)
            const previewRows = validatedData.slice(0, 10);
            tbody.innerHTML = previewRows.map((row, idx) => {
                const rowClass = row._valid ? '' : 'style="background: var(--danger-light);"';
                return `
                    <tr ${rowClass}>
                        <td class="row-number">${row._rowIndex}</td>
                        <td>${row.nombre || '<span class="cell-error">-</span>'}</td>
                        <td>${row.precio ? formatCurrency(row.precio) : '<span class="cell-error">-</span>'}</td>
                        <td>${row.stock ?? '<span class="cell-error">-</span>'}</td>
                        <td>${row.costo ? formatCurrency(row.costo) : '-'}</td>
                        <td>${row.referencia_sku || '-'}</td>
                        <td>${row.categoria || '-'}</td>
                    </tr>
                `;
            }).join('');

            // Mostrar mensaje si hay más filas
            if (validatedData.length > 10) {
                tbody.innerHTML += `
                    <tr>
                        <td colspan="7" class="more-rows">
                            ... y ${validatedData.length - 10} productos más
                        </td>
                    </tr>
                `;
            }

            previewSection.style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
        }

        function showValidationError(message) {
            const box = document.getElementById('validationBox');
            box.className = 'validation-box error';
            box.innerHTML = `<i class="bi bi-exclamation-triangle"></i> ${message}`;
        }

        function showValidationSuccess(message) {
            const box = document.getElementById('validationBox');
            box.className = 'validation-box success';
            box.innerHTML = `<i class="bi bi-check-circle"></i> ${message}`;
        }

        // ==========================================
        // CARGA AL SERVIDOR
        // ==========================================
        async function startUpload() {
            const validProducts = validatedData.filter(r => r._valid);
            
            if (validProducts.length === 0) {
                showToast('No hay productos válidos para cargar', 'error');
                return;
            }

            if (businessId === '0') {
                showToast('Selecciona un negocio primero', 'error');
                return;
            }

            const btn = document.getElementById('btnUpload');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Cargando...';

            const progressSection = document.getElementById('progressSection');
            progressSection.style.display = 'block';
            document.getElementById('progressBar').style.width = '50%';
            document.getElementById('progressPercent').textContent = '50%';
            document.getElementById('progressText').textContent = `Enviando ${validProducts.length} productos...`;

            try {
                // ★ CORREGIDO: Enviar todos los productos en un solo request
                const payload = {
                    negocio_id: Number(businessId),
                    sucursal_id: Number(branchId),
                    productos: validProducts.map(p => ({
                        nombre: p.nombre,
                        precio: p.precio,
                        stock: p.stock,
                        costo: p.costo || 0,
                        sku: p.referencia_sku || '',
                        categoria: p.categoria || 'General',
                        descripcion: p.descripcion || ''
                    }))
                };

                console.log('📤 Enviando payload:', payload);
                console.log('📡 Endpoint:', `${API_URL}/control/inventario/carga-masiva`);

                // ★ CORREGIDO: Usar el endpoint correcto
                const response = await fetch(`${API_URL}/control/inventario/carga-masiva`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-User-ID': userId,
                        'X-Business-ID': businessId
                    },
                    credentials: 'include', // ★ Importante para @login_required
                    body: JSON.stringify(payload)
                });

                console.log('📥 Response status:', response.status);

                // ★ Manejar errores de autenticación
                if (response.status === 401) {
                    throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
                }

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `Error HTTP ${response.status}`);
                }

                document.getElementById('progressBar').style.width = '100%';
                document.getElementById('progressPercent').textContent = '100%';

                const result = await response.json();
                console.log('📥 Respuesta:', result);

                if (result.success) {
                    showResults(
                        validProducts.length,
                        result.total_procesados || validProducts.length,
                        result.errores?.length || 0,
                        result.errores || []
                    );
                    showToast(`✅ ${result.message}`, 'success');
                } else {
                    throw new Error(result.message || 'Error del servidor');
                }

            } catch (e) {
                console.error('❌ Error:', e);
                showToast(`Error: ${e.message}`, 'error');
                
                document.getElementById('progressSection').style.display = 'none';
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-cloud-upload"></i> Cargar al Inventario';
                return;
            }

            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-cloud-upload"></i> Cargar al Inventario';
        }

        // ==========================================
        // MOSTRAR RESULTADOS
        // ==========================================
        function showResults(total, success, errorCount, errorDetails) {
            document.getElementById('previewSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'block';

            document.getElementById('resultTotal').textContent = total;
            document.getElementById('resultSuccess').textContent = success;
            document.getElementById('resultErrors').textContent = errorCount;

            // Mostrar errores si los hay
            if (errorDetails && errorDetails.length > 0) {
                console.log('⚠️ Errores del servidor:');
                errorDetails.forEach(err => {
                    console.log(`   - ${err}`);
                });
            }
        }

        // ==========================================
        // UTILIDADES
        // ==========================================
        function resetUpload() {
            document.getElementById('previewSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('progressSection').style.display = 'none';
            document.getElementById('fileInput').value = '';
            rawData = [];
            validatedData = [];
        }

        function goToInventory() {
            // Intentar navegar al inventario
            if (window.parent !== window) {
                window.parent.postMessage({ action: 'navigate', module: 'inventario' }, '*');
            } else {
                window.location.href = 'inventario.html';
            }
        }

        function formatCurrency(amount) {
            return new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 0
            }).format(amount || 0);
        }

        function showToast(message, type = '') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = `toast ${type} show`;
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
    </script>
</body>
</html>