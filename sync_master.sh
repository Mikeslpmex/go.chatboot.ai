#!/bin/bash

################################################################################
# 🚀 NEURAFORGE AI - SINCRONIZADOR MAESTRO
################################################################################
# Sincroniza múltiples repositorios y maneja conflictos automáticamente
# Uso: ./sync_master.sh [repo] [mensaje]
################################################################################

set -e

# ============================================================================
# COLORES PARA TERMINAL
# ============================================================================
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
REPOS=(
  "Mikeslpmex/go.developers.ai"
  "Mikeslpmex/NeuraforgeAI-Suite"
  "Mikeslpmex/NeuraforgeAI"
  "Mikeslpmex/go.chatboot.ai"
  "Mikeslpmex/appcodex.ai"
)

MAIN_BRANCHES=("main" "master")
TIMESTAMP=$(date +'%Y-%m-%d_%H-%M-%S')
LOG_FILE="sync_${TIMESTAMP}.log"

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC} $1"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ============================================================================
# DETECCIÓN DE RAMA PRINCIPAL
# ============================================================================

get_main_branch() {
    local repo_dir=$1
    cd "$repo_dir" 2>/dev/null || return 1
    
    for branch in "${MAIN_BRANCHES[@]}"; do
        if git rev-parse --verify "$branch" >/dev/null 2>&1; then
            echo "$branch"
            return 0
        fi
    done
    
    # Fallback: obtener la rama por defecto del servidor
    git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's/origin\///' || echo "main"
}

# ============================================================================
# MANEJO DE CONFLICTOS
# ============================================================================

resolve_conflicts() {
    local repo_dir=$1
    local strategy=${2:-"ours"}  # "ours", "theirs", o "manual"
    
    cd "$repo_dir" || return 1
    
    local conflicted_files=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflicted_files" ]; then
        return 0  # Sin conflictos
    fi
    
    print_warning "Se detectaron conflictos en: $repo_dir"
    
    case $strategy in
        "ours")
            print_info "Resolviendo conflictos usando estrategia 'ours'..."
            echo "$conflicted_files" | while read -r file; do
                git checkout --ours "$file"
                git add "$file"
            done
            print_success "Conflictos resueltos (versión local)"
            ;;
        "theirs")
            print_info "Resolviendo conflictos usando estrategia 'theirs'..."
            echo "$conflicted_files" | while read -r file; do
                git checkout --theirs "$file"
                git add "$file"
            done
            print_success "Conflictos resueltos (versión remota)"
            ;;
        "manual")
            print_error "Se requiere resolución manual de conflictos:"
            echo "$conflicted_files"
            return 1
            ;;
    esac
}

# ============================================================================
# SINCRONIZACIÓN DE UN REPOSITORIO
# ============================================================================

sync_repository() {
    local repo_path=$1
    local custom_message=$2
    local repo_name=$(basename "$repo_path")
    
    if [ ! -d "$repo_path/.git" ]; then
        print_error "No es un repositorio Git: $repo_path"
        log "ERROR: $repo_path no es un repositorio"
        return 1
    fi
    
    print_header "Sincronizando: $repo_name"
    log "=== Sincronización iniciada: $repo_name ==="
    
    cd "$repo_path" || return 1
    
    # 1. Obtener rama principal
    local main_branch=$(get_main_branch "$repo_path")
    print_info "Rama principal detectada: $main_branch"
    
    # 2. Verificar estado
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Hay cambios sin stagear"
        git status --short
    fi
    
    # 3. Configurar estrategia de pull
    git config pull.rebase false 2>/dev/null || true
    
    # 4. Agregar cambios
    print_info "Agregando cambios..."
    git add . 2>/dev/null || true
    
    # 5. Crear commit
    local commit_msg="${custom_message:-Actualización automática - $TIMESTAMP}"
    if [ -n "$(git status --porcelain)" ]; then
        print_info "Creando commit: '$commit_msg'"
        git commit -m "$commit_msg" || print_warning "No hay cambios nuevos para commit"
        log "Commit creado: $commit_msg"
    else
        print_info "Sin cambios para commitear"
    fi
    
    # 6. Sincronizar con remoto
    print_info "Traiendo cambios desde GitHub..."
    if git pull origin "$main_branch" 2>&1; then
        print_success "Pull completado exitosamente"
        log "Pull completado: $main_branch"
    else
        print_warning "Conflicto detectado. Intentando resolución automática..."
        
        if ! resolve_conflicts "$repo_path" "ours"; then
            print_error "No se pudieron resolver automáticamente los conflictos"
            print_warning "Abortando pull para este repositorio..."
            git merge --abort 2>/dev/null || git rebase --abort 2>/dev/null || true
            log "ERROR: Conflictos no resueltos en $repo_name"
            return 1
        fi
        
        # Completar merge/rebase después de resolver conflictos
        if git diff --name-only --diff-filter=U | grep -q . 2>/dev/null; then
            git commit --no-edit -m "Merge: Resolución automática de conflictos" || true
        fi
    fi
    
    # 7. Pushear cambios
    print_info "Subiendo cambios a GitHub..."
    if git push origin "$main_branch" 2>&1; then
        print_success "Push completado exitosamente"
        log "Push completado: $main_branch"
    else
        print_error "Error al hacer push. Verifica permisos y configuración remota."
        log "ERROR: Push fallido en $repo_name"
        return 1
    fi
    
    print_success "✨ $repo_name sincronizado correctamente"
    echo ""
}

# ============================================================================
# SINCRONIZACIÓN MÚLTIPLE
# ============================================================================

sync_all() {
    print_header "🌐 SINCRONIZADOR NEURAFORGE - Modo Múltiple"
    print_info "Total de repositorios a sincronizar: ${#REPOS[@]}"
    echo ""
    
    local successful=0
    local failed=0
    
    for repo in "${REPOS[@]}"; do
        if sync_repository "$repo" "$1"; then
            ((successful++))
        else
            ((failed++))
        fi
    done
    
    echo ""
    print_header "📊 RESUMEN DE SINCRONIZACIÓN"
    print_success "Repositorios exitosos: $successful"
    print_error "Repositorios con errores: $failed"
    echo -e "${BLUE}Log completo: $LOG_FILE${NC}"
}

# ============================================================================
# VALIDACIÓN DE CREDENTIALS GIT
# ============================================================================

verify_git_config() {
    print_info "Verificando configuración de Git..."
    
    if [ -z "$(git config --global user.name)" ]; then
        print_warning "Usuario Git no configurado. Configurando..."
        git config --global user.name "NeuraforgeAI Bot"
        git config --global user.email "dev@neuraforge.ai"
    fi
    
    print_success "Configuración de Git validada"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_header "🚀 INICIANDO SINCRONIZADOR NEURAFORGE"
    
    verify_git_config
    
    if [ $# -gt 0 ] && [ "$1" != "all" ]; then
        # Sincronizar un repositorio específico
        local repo_path=$(pwd)
        if [ -d "$1/.git" ]; then
            repo_path="$1"
        fi
        sync_repository "$repo_path" "$2"
    else
        # Sincronizar todos
        sync_all "$1"
    fi
    
    print_success "¡Sincronización completada!"
    log "=== Sincronización finalizada exitosamente ==="
}

# Ejecutar
main "$@"
