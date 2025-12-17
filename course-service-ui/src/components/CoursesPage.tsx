import CoursesTable from "./CoursesTable";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";

const CoursesPage = () => {
  return (
    <div className="max-w-[1400px] mx-auto p-5 grid gap-6">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbPage>Courses</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <CoursesTable />
    </div>
  );
};

export default CoursesPage;
