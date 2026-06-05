import { AnimatePresence, motion } from "framer-motion";
import { useState, lazy, Suspense } from "react";
import { Layout } from "./components/Layout";

const Dashboard = lazy(() => import("./pages/Dashboard").then((module) => ({ default: module.Dashboard })));
const Monitoring = lazy(() => import("./pages/Monitoring").then((module) => ({ default: module.Monitoring })));
const Alerts = lazy(() => import("./pages/Alerts").then((module) => ({ default: module.Alerts })));
const Rul = lazy(() => import("./pages/Rul").then((module) => ({ default: module.Rul })));
const Analytics = lazy(() => import("./pages/Analytics").then((module) => ({ default: module.Analytics })));
const Explainability = lazy(() => import("./pages/Explainability").then((module) => ({ default: module.Explainability })));
const History = lazy(() => import("./pages/History").then((module) => ({ default: module.History })));

const pages = {
  dashboard: Dashboard,
  monitoring: Monitoring,
  alertes: Alerts,
  rul: Rul,
  analytics: Analytics,
  explainability: Explainability,
  historique: History
};

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-copper"></div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const Page = pages[page];
  return (
    <Layout page={page} setPage={setPage}>
      <AnimatePresence mode="wait">
        <motion.div key={page} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
          <Suspense fallback={<PageLoader />}>
            <Page />
          </Suspense>
        </motion.div>
      </AnimatePresence>
    </Layout>
  );
}
