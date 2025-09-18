# GitHub Actions - Automatización de CI/CD

Este directorio contiene los workflows de GitHub Actions que automatizan el proceso de integración continua y despliegue para el proyecto de Recetario.

## 📋 Workflows Implementados

### 1. Merge de Ramas de Funcionalidad a Develop
**Archivo:** `merge-feature-to-develop.yml`

**Trigger:** Push a cualquier rama que comience con `historia`

**Palabra clave:** `LISTO_PARA_DESARROLLO`

**Proceso:**
1. ✅ Detecta push en ramas `historia**`
2. ✅ Verifica palabra clave en mensaje de commit
3. ✅ Actualiza rama de funcionalidad con develop
4. ✅ Ejecuta pruebas unitarias
5. ✅ Ejecuta análisis de cobertura
6. ✅ Mezcla rama de funcionalidad a develop (si pruebas pasan)

**Uso:**
```bash
git commit -m "Implementar nueva funcionalidad LISTO_PARA_DESARROLLO"
git push origin historia-mi-funcionalidad
```

### 2. Creación de Release y Merge a Master
**Archivo:** `create-release-and-merge-to-master.yml`

**Trigger:** Push a rama `develop`

**Palabra clave:** `CREAR_RELEASE`

**Proceso:**
1. ✅ Detecta push en rama `develop`
2. ✅ Verifica palabra clave en mensaje de commit
3. ✅ Crea rama `release` temporal
4. ✅ Mezcla develop en release
5. ✅ Ejecuta pruebas unitarias en release
6. ✅ Ejecuta análisis de cobertura en release
7. ✅ Mezcla release a master (si pruebas pasan)
8. ✅ Crea tag de release con timestamp
9. ✅ Elimina rama release temporal

**Uso:**
```bash
git commit -m "Preparar versión estable CREAR_RELEASE"
git push origin develop
```

## 🔧 Configuración Requerida

### Permisos del Repositorio
Asegúrate de que el repositorio tenga los siguientes permisos habilitados:
- ✅ Actions: Read and write permissions
- ✅ Contents: Read and write permissions
- ✅ Pull requests: Read permissions

### Tokens de Acceso
Los workflows utilizan automáticamente `secrets.GITHUB_TOKEN` que GitHub proporciona por defecto.

## 📝 Convenciones de Commits

### Para Merge a Develop
```
git commit -m "Descripción de la funcionalidad LISTO_PARA_DESARROLLO"
```

### Para Crear Release
```
git commit -m "Preparar versión X.X.X CREAR_RELEASE"
```

## 🚀 Flujo de Trabajo Recomendado

### Desarrollo de Funcionalidades
1. Crear rama desde develop: `git checkout -b historia-mi-funcionalidad`
2. Desarrollar funcionalidad
3. Commit con palabra clave: `git commit -m "Mi funcionalidad LISTO_PARA_DESARROLLO"`
4. Push: `git push origin historia-mi-funcionalidad`
5. El workflow automáticamente:
   - Actualiza tu rama con develop
   - Ejecuta pruebas
   - Mezcla a develop si todo está OK

### Creación de Release
1. Asegúrate de estar en develop: `git checkout develop`
2. Commit de release: `git commit -m "Release v1.0.0 CREAR_RELEASE"`
3. Push: `git push origin develop`
4. El workflow automáticamente:
   - Crea rama release temporal
   - Ejecuta pruebas
   - Mezcla a master si todo está OK
   - Crea tag de release
   - Limpia rama temporal

## 🔍 Monitoreo

### Verificar Estado de Workflows
- Ve a la pestaña "Actions" en tu repositorio GitHub
- Revisa el estado de cada workflow
- Los logs detallados te mostrarán cada paso del proceso

### Tags de Release
Los tags se crean automáticamente con formato: `release_YYYYMMDD_HHMMSS`

## ⚠️ Consideraciones Importantes

1. **Palabras Clave:** Deben estar exactamente como se especifica (case-sensitive)
2. **Pruebas:** Si las pruebas fallan, el merge se cancela automáticamente
3. **Conflictos:** Si hay conflictos de merge, el workflow fallará
4. **Permisos:** Asegúrate de tener permisos de escritura en el repositorio

## 🛠️ Tecnologías Utilizadas

- **GitHub Actions:** Automatización de CI/CD
- **Python:** Ejecución de pruebas unitarias
- **Coverage:** Análisis de cobertura de código
- **Direct Merge Action:** Merge automático entre ramas
- **Ubuntu Latest:** Entorno de ejecución

## 📞 Soporte

Si encuentras problemas con los workflows:
1. Revisa los logs en la pestaña "Actions"
2. Verifica que las palabras clave estén correctas
3. Asegúrate de que las pruebas pasen localmente
4. Confirma que tienes los permisos necesarios
