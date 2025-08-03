# 🇮🇳 Bond Liquidity Heatmap - Indian Markets

A real-time bond liquidity monitoring platform for Indian markets, helping traders identify depth and avoid over-paying on odd-lot trades.

## 🎯 Problem Statement

Corporate-bond traders in India can see trades within 15 minutes (SEBI rules), but desks can't quickly identify where real buying/selling depth exists. Wrong guesses lead to over-paying or under-selling on odd-lot trades.

## 🚀 Solution

A simple web screen that lights up green, yellow, or red across ratings (AAA, AA, A) and maturity buckets (0-1y, 1-3y, 3-5y, 5-10y, 10y+). Each tile shows "Plenty of depth here—tight spreads" or "Liquidity just dried up—be careful." Refreshes every 15 minutes.

## ✨ Features

- **Real-time Depth Scoring**: Volume ÷ (Spread × Time Since Last Trade)
- **Color-coded Heatmap**: Green (high liquidity), Amber (moderate), Red (low liquidity)
- **Comprehensive Coverage**: 240 bonds across 6 ratings × 5 tenors
- **Live Updates**: 15-minute refresh cycles
- **Market Insights**: Top liquidity by rating and tenor
- **Data Regeneration**: One-click fresh data generation
- **Professional UI**: Trading floor-ready interface

## 🏗️ Architecture

### Current Prototype
- **Data Generation**: Synthetic trade data with realistic patterns
- **Depth Scoring**: Advanced algorithm with rolling averages
- **UI**: Streamlit-based web application
- **Database**: SQLite for development

### Production Roadmap
- **Phase 1**: Real F-TRAC data integration
- **Phase 2**: SMS/Slack alerts
- **Phase 3**: REST API and data feeds
- **Phase 4**: Multi-tenant architecture

## 🛠️ Installation

### Prerequisites
- Windows 10/11
- Python 3.11+ added to PATH

### Quick Start
```bash
# Clone the repository
git clone https://github.com/StackCraft007/Bond-Liquidity-Heatmap.git
cd Bond-Liquidity-Heatmap

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate sample data and launch
streamlit run src\ui.py
```

### Alternative: Automated Setup
```bash
# Run the automated setup script
run.bat
```

## 📊 Usage

1. **Launch the Application**: `streamlit run src\ui.py`
2. **Access the UI**: Open http://localhost:8501 in your browser and https://stackcraft007-bond-liquidity-heatmap-srcui-y2g42e.streamlit.app/  on streamlit
3. **Generate Data**: Click "🔄 Regenerate Data" in the sidebar
4. **View Heatmap**: See color-coded liquidity depth across ratings and tenors
5. **Monitor Updates**: Auto-refresh every 15 minutes

## 📈 Business Model

| Package | Target | Price | Features |
|---------|--------|-------|----------|
| **Starter** | Small prop desks, wealth-techs | ₹35k/month/seat | Basic heatmap, 15-min refresh |
| **Pro** | NBFC & bank trading floors | ₹2L/month + 0.5bps | Full features, alerts, API access |
| **Enterprise** | Mutual funds, index builders | ₹40L/year | Raw data feed, custom integrations |

## 🏆 Competitive Advantage

### vs. Bloomberg/Refinitiv
- ✅ 15-minute vs 30-minute lag
- ✅ ₹2L vs ₹20L+ per terminal
- ✅ India-focused coverage
- ✅ Real-time alerts

### vs. Indian Data Vendors
- ✅ Real-time vs end-of-day
- ✅ Depth scoring vs raw data
- ✅ Interactive UI vs CSV files
- ✅ Alert system

## 🔧 Technical Stack

- **Backend**: Python 3.11+, FastAPI, Streamlit
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Data Processing**: Pandas, NumPy
- **Cloud**: AWS (EC2, RDS, S3)
- **Integrations**: Twilio (SMS), Slack, SendGrid

## 📁 Project Structure

```
Bond-Liquidity-Heatmap/
├── src/
│   ├── generate_data.py      # Synthetic data generation
│   ├── ingest.py            # Database ingestion
│   ├── compute_metrics.py   # Depth scoring algorithm
│   └── ui.py               # Streamlit web interface
├── data/                   # Generated CSV files
├── requirements.txt        # Python dependencies
├── run.bat               # Automated setup script
├── BUSINESS_ROADMAP.md   # 12-week development plan
└── README.md            # This file
```

## 🚀 Development Roadmap

### Immediate (Next 2 weeks)
- [x] Fix current prototype bugs
- [ ] Set up production database
- [ ] Create F-TRAC data parser
- [ ] Implement real depth scoring
- [ ] Build basic authentication

### Short-term (Weeks 3-6)
- [ ] Real-time data pipeline
- [ ] Enhanced UI with alerts
- [ ] SMS/Slack integration
- [ ] Multi-tenant architecture
- [ ] Performance optimization

### Medium-term (Weeks 7-12)
- [ ] REST API development
- [ ] CSV data feeds
- [ ] Pilot program launch
- [ ] Customer feedback integration
- [ ] Production deployment

## 📊 Success Metrics

### Technical KPIs
- Data latency < 15 minutes
- UI response time < 2 seconds
- 99.9% uptime
- Alert delivery < 30 seconds

### Business KPIs
- 10 paying customers by Month 6
- ₹50L ARR by Month 12
- 80% customer retention
- 5+ strategic partnerships

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Contact

- **Project**: Bond Liquidity Heatmap
- **Organization**: StackCraft
- **Email**: [Your Email]
- **LinkedIn**: [Your LinkedIn]

---

**Bottom Line**: Regulations have opened data floodgates; the desk that spots vanishing liquidity first wins. This lightweight heatmap turns raw prints into a color-coded "depth radar" - cheap to build, priced to pay for itself in a single tightened trade.
