export interface Course {
  course_id: string;
  course_name: string;
  term_id: string;
}

export interface CoursesResponse {
  courses: Course[];
}

export interface CourseDetails extends Course {
  profiles?: string[];
  description?: string;
}

export interface CourseMember {
  username: string;
  role: string;
  deletable?: boolean;
}

export interface Image {
  name: string;
  tag: string;
  pullPolicy: string;
}

export interface Resources {
  cpu_guarantee: string;
  cpu_limit: string;
  mem_guarantee: string;
  mem_limit: string;
}

export interface Runtime {
  image: Image;
  resources: Resources;
  environment: Record<string, string>;
}

export interface Profile {
  name: string;
  display_name: string;
  runtime: Runtime;
}
