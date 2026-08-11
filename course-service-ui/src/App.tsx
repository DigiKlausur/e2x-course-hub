import { Routes, Route, Navigate } from "react-router-dom";
import { CoursesPage } from "./components/courses/CoursesPage";
import { CoursePage } from "./components/course/CoursePage";
import { TermPage } from "./components/term/TermPage";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-[#f5f7fb]">
      <Routes>
        <Route path="/" element={<CoursesPage />} />
        <Route path="/course/:courseId/*" element={<CoursePage />} />
        <Route path="/course/:courseId/term/:termId/*" element={<TermPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
