import { AppHeader } from './components/layout/AppHeader';
import { PageContainer } from './components/layout/PageContainer';
import { DebuggerPage } from './pages/DebuggerPage';
import './index.css';

export default function App() {
  return (
    <div className="app-root">
      <AppHeader />
      <PageContainer>
        <DebuggerPage />
      </PageContainer>
    </div>
  );
}
