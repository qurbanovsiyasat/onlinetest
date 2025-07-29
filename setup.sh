#!/bin/bash

# Squiz Platform Setup Script
# Bu script local development ortamını hazırlar

echo "🚀 Squiz Platform Kurulum Başlatılıyor..."

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hata kontrolü fonksiyonu
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Hata: $1${NC}"
        exit 1
    fi
}

# Gerekli araçları kontrol et
echo -e "${BLUE}🔍 Gerekli araçlar kontrol ediliyor...${NC}"

# Node.js kontrolü
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js bulunamadı. Lütfen Node.js 18+ yükleyin.${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js 18+ gerekli. Mevcut versiyon: $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v) bulundu${NC}"

# npm kontrolü
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm bulunamadı.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm $(npm -v) bulundu${NC}"

# Docker kontrolü
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker bulunamadı. Backend için Docker gerekli.${NC}"
    echo -e "${YELLOW}   Docker'ı https://docker.com adresinden yükleyebilirsiniz.${NC}"
else
    echo -e "${GREEN}✅ Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1) bulundu${NC}"
fi

# Docker Compose kontrolü
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose bulunamadı.${NC}"
else
    echo -e "${GREEN}✅ Docker Compose bulundu${NC}"
fi

# Environment dosyalarını oluştur
echo -e "${BLUE}📝 Environment dosyaları oluşturuluyor...${NC}"

# .env.local dosyası oluştur
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
# Local Development Environment Variables
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_APP_NAME=Squiz Platform
NEXT_PUBLIC_DEBUG=true
EOF
    echo -e "${GREEN}✅ .env.local dosyası oluşturuldu${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local dosyası zaten mevcut${NC}"
fi

# Backend .env dosyası oluştur
if [ ! -f "backend/.env" ]; then
    mkdir -p backend
    cat > backend/.env << EOF
# Backend Environment Variables
MONGODB_URL=mongodb://localhost:27017/squiz_db
JWT_SECRET=your-super-secret-jwt-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEBUG=true
ENVIRONMENT=development
EOF
    echo -e "${GREEN}✅ backend/.env dosyası oluşturuldu${NC}"
else
    echo -e "${YELLOW}⚠️  backend/.env dosyası zaten mevcut${NC}"
fi

# Package.json kontrolü ve dependencies kurulumu
echo -e "${BLUE}📦 Dependencies kuruluyor...${NC}"

if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json bulunamadı. Proje dizininde olduğunuzdan emin olun.${NC}"
    exit 1
fi

# Node modules kurulumu
echo -e "${BLUE}📦 Frontend dependencies kuruluyor...${NC}"
npm install
check_error "Frontend dependencies kurulumu başarısız"

echo -e "${GREEN}✅ Frontend dependencies kuruldu${NC}"

# Backend dependencies kurulumu (Python)
if [ -f "backend/requirements.txt" ]; then
    echo -e "${BLUE}🐍 Backend dependencies kontrol ediliyor...${NC}"
    
    # Python kontrolü
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python3 bulundu${NC}"
    else
        echo -e "${YELLOW}⚠️  Python3 bulunamadı. Backend için Python 3.8+ gerekli.${NC}"
    fi
    
    # pip kontrolü
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✅ pip3 bulundu${NC}"
    else
        echo -e "${YELLOW}⚠️  pip3 bulunamadı.${NC}"
    fi
fi

# MongoDB kurulumu kontrolü
echo -e "${BLUE}🍃 MongoDB kontrol ediliyor...${NC}"

if command -v mongod &> /dev/null; then
    echo -e "${GREEN}✅ MongoDB bulundu${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB bulunamadı.${NC}"
    echo -e "${YELLOW}   Docker ile MongoDB çalıştırabilirsiniz: docker run -d -p 27017:27017 mongo${NC}"
fi

# Git hooks kurulumu
echo -e "${BLUE}🔧 Git hooks kuruluyor...${NC}"

if [ -d ".git" ]; then
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 Pre-commit checks çalıştırılıyor..."

# TypeScript type check
npm run type-check
if [ $? -ne 0 ]; then
    echo "❌ TypeScript type check başarısız"
    exit 1
fi

# Linting
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Linting başarısız"
    exit 1
fi

echo "✅ Pre-commit checks başarılı"
EOF
    
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✅ Git hooks kuruldu${NC}"
else
    echo -e "${YELLOW}⚠️  Git repository bulunamadı${NC}"
fi

# Development scripts oluştur
echo -e "${BLUE}📜 Development scripts oluşturuluyor...${NC}"

# Start script
cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Squiz Platform Development Server Başlatılıyor..."

# Backend'i arka planda başlat (Docker ile)
if command -v docker-compose &> /dev/null; then
    echo "🐳 Backend (Docker) başlatılıyor..."
    docker-compose up -d backend mongodb
    sleep 5
else
    echo "⚠️  Docker Compose bulunamadı. Backend'i manuel başlatmanız gerekebilir."
fi

# Frontend'i başlat
echo "⚛️  Frontend başlatılıyor..."
npm run dev
EOF

chmod +x start-dev.sh

# Stop script
cat > stop-dev.sh << 'EOF'
#!/bin/bash
echo "🛑 Squiz Platform Development Server Durduruluyor..."

# Docker containers'ı durdur
if command -v docker-compose &> /dev/null; then
    docker-compose down
    echo "✅ Backend durduruldu"
else
    echo "⚠️  Docker Compose bulunamadı"
fi

# Node processes'i durdur
pkill -f "next dev"
echo "✅ Frontend durduruldu"
EOF

chmod +x stop-dev.sh

echo -e "${GREEN}✅ Development scripts oluşturuldu${NC}"

# Database seed script
echo -e "${BLUE}🌱 Database seed script oluşturuluyor...${NC}"

cat > seed-database.sh << 'EOF'
#!/bin/bash
echo "🌱 Database seed işlemi başlatılıyor..."

# MongoDB'nin çalıştığını kontrol et
if ! nc -z localhost 27017; then
    echo "❌ MongoDB'ye bağlanılamıyor. Lütfen MongoDB'yi başlatın."
    exit 1
fi

# Seed data'yı MongoDB'ye yükle
if [ -f "mongo-init.js" ]; then
    mongo squiz_db mongo-init.js
    echo "✅ Database seed tamamlandı"
else
    echo "⚠️  mongo-init.js dosyası bulunamadı"
fi
EOF

chmod +x seed-database.sh

# Test script
cat > run-tests.sh << 'EOF'
#!/bin/bash
echo "🧪 Test suite çalıştırılıyor..."

# Frontend tests
echo "⚛️  Frontend testleri..."
npm run test

# Backend tests (eğer varsa)
if [ -f "backend/pytest.ini" ] || [ -f "backend/test_*.py" ]; then
    echo "🐍 Backend testleri..."
    cd backend && python -m pytest
    cd ..
fi

echo "✅ Tüm testler tamamlandı"
EOF

chmod +x run-tests.sh

echo -e "${GREEN}✅ Utility scripts oluşturuldu${NC}"

# VSCode ayarları
echo -e "${BLUE}⚙️  VSCode ayarları oluşturuluyor...${NC}"

mkdir -p .vscode

# VSCode settings
cat > .vscode/settings.json << 'EOF'
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  },
  "tailwindCSS.experimental.classRegex": [
    ["cva\$$([^)]*)\$$", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cx\$$([^)]*)\$$", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ]
}
EOF

# VSCode extensions
cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-python.python",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-json"
  ]
}
EOF

# VSCode launch configuration
cat > .vscode/launch.json << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "cwd": "${workspaceFolder}",
      "runtimeExecutable": "node",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
EOF

echo -e "${GREEN}✅ VSCode ayarları oluşturuldu${NC}"

# Kurulum özeti
echo -e "\n${GREEN}🎉 Squiz Platform kurulumu tamamlandı!${NC}\n"

echo -e "${BLUE}📋 Kurulum Özeti:${NC}"
echo -e "   ✅ Environment dosyaları oluşturuldu"
echo -e "   ✅ Dependencies kuruldu"
echo -e "   ✅ Development scripts hazırlandı"
echo -e "   ✅ VSCode ayarları yapılandırıldı"
echo -e "   ✅ Git hooks kuruldu"

echo -e "\n${BLUE}🚀 Başlatma Komutları:${NC}"
echo -e "   ${YELLOW}Development server:${NC} ./start-dev.sh veya npm run dev"
echo -e "   ${YELLOW}Backend + Frontend:${NC} docker-compose up"
echo -e "   ${YELLOW}Database seed:${NC} ./seed-database.sh"
echo -e "   ${YELLOW}Testleri çalıştır:${NC} ./run-tests.sh"

echo -e "\n${BLUE}🌐 Erişim Adresleri:${NC}"
echo -e "   ${YELLOW}Frontend:${NC} http://localhost:3000"
echo -e "   ${YELLOW}Backend API:${NC} http://localhost:8001"
echo -e "   ${YELLOW}API Docs:${NC} http://localhost:8001/docs"
echo -e "   ${YELLOW}MongoDB:${NC} mongodb://localhost:27017"

echo -e "\n${BLUE}👤 Demo Hesap:${NC}"
echo -e "   ${YELLOW}Email:${NC} admin@squiz.com"
echo -e "   ${YELLOW}Şifre:${NC} admin123"

echo -e "\n${BLUE}📚 Yararlı Komutlar:${NC}"
echo -e "   ${YELLOW}Logs görüntüle:${NC} docker-compose logs -f"
echo -e "   ${YELLOW}Database reset:${NC} docker-compose down -v && docker-compose up"
echo -e "   ${YELLOW}Production build:${NC} npm run build"

echo -e "\n${GREEN}✨ Squiz Platform kullanıma hazır!${NC}"
echo -e "${BLUE}Başlamak için: ${YELLOW}./start-dev.sh${NC} komutunu çalıştırın\n"
