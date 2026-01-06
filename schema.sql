PRAGMA foreign_keys = ON;

-- ========== Core org structure ==========

CREATE TABLE workspaces (
  workspace_id TEXT PRIMARY KEY,                 -- UUID/GID-like
  name         TEXT NOT NULL,
  domain       TEXT,                             -- verified domain for orgs (optional)
  is_organization INTEGER NOT NULL DEFAULT 1,     -- 1=true, 0=false
  created_at   TEXT NOT NULL
);

CREATE TABLE teams (
  team_id      TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name         TEXT NOT NULL,
  description  TEXT,
  visibility   TEXT NOT NULL DEFAULT 'organization',  -- organization/private
  created_at   TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
);

CREATE TABLE users (
  user_id      TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  full_name    TEXT NOT NULL,
  email        TEXT NOT NULL,
  title        TEXT,                             -- job title
  department   TEXT,                             -- Eng/Marketing/Ops etc.
  location     TEXT,
  is_active    INTEGER NOT NULL DEFAULT 1,
  role         TEXT NOT NULL DEFAULT 'member',    -- member/admin (simplified)
  created_at   TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  UNIQUE (workspace_id, email)
);

CREATE TABLE team_memberships (
  team_id    TEXT NOT NULL,
  user_id    TEXT NOT NULL,
  is_team_admin INTEGER NOT NULL DEFAULT 0,
  joined_at  TEXT NOT NULL,
  PRIMARY KEY (team_id, user_id),
  FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ========== Projects & sections ==========

CREATE TABLE projects (
  project_id   TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  team_id      TEXT,                             -- optional: some projects might not belong to a single team
  name         TEXT NOT NULL,
  description  TEXT,
  privacy      TEXT NOT NULL DEFAULT 'organization', -- organization/private
  layout       TEXT NOT NULL DEFAULT 'list',      -- list/board (sections still exist either way) [web:32]
  status       TEXT NOT NULL DEFAULT 'active',    -- active/archived
  color        TEXT,
  created_by   TEXT,
  created_at   TEXT NOT NULL,
  archived_at  TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE sections (
  section_id   TEXT PRIMARY KEY,
  project_id   TEXT NOT NULL,
  name         TEXT NOT NULL,
  sort_order   INTEGER NOT NULL,                 -- order within project
  created_at   TEXT NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
  UNIQUE (project_id, sort_order),
  UNIQUE (project_id, name)
);

-- ========== Tasks & hierarchy ==========

CREATE TABLE tasks (
  task_id        TEXT PRIMARY KEY,
  workspace_id   TEXT NOT NULL,
  project_id     TEXT NOT NULL,
  section_id     TEXT,                           -- tasks can be in a section; sections are subdivisions of a project [web:32]
  parent_task_id TEXT,                           -- NULL for top-level tasks; non-NULL => subtask
  name           TEXT NOT NULL,
  description    TEXT,                           -- notes
  created_by     TEXT,
  assignee_id    TEXT,                           -- NULL means unassigned
  due_on         TEXT,                           -- DATE string (YYYY-MM-DD)
  start_on       TEXT,                           -- optional
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL,
  completed      INTEGER NOT NULL DEFAULT 0,
  completed_at   TEXT,
  priority       TEXT,                           -- optional “standardized” field (you can also model as custom field)
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
  FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE SET NULL,
  FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
  FOREIGN KEY (assignee_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_section ON tasks(section_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_due ON tasks(due_on);

-- ========== Comments (stories) ==========

CREATE TABLE comments (
  comment_id   TEXT PRIMARY KEY,
  task_id      TEXT NOT NULL,
  author_id    TEXT,
  body         TEXT NOT NULL,
  created_at   TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_comments_task ON comments(task_id);

-- ========== Custom fields ==========
-- Asana supports user-specified custom fields attached to tasks/projects/etc. [web:2]

CREATE TABLE custom_field_definitions (
  custom_field_id TEXT PRIMARY KEY,
  workspace_id    TEXT NOT NULL,
  name            TEXT NOT NULL,
  field_type      TEXT NOT NULL,                 -- enum: text/number/enum/multi_enum/date/people
  description     TEXT,
  created_by      TEXT,
  created_at      TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
  UNIQUE (workspace_id, name)
);

-- Options for enum fields (Priority: High/Med/Low etc.)
CREATE TABLE custom_field_enum_options (
  option_id       TEXT PRIMARY KEY,
  custom_field_id TEXT NOT NULL,
  name            TEXT NOT NULL,
  color           TEXT,
  sort_order      INTEGER NOT NULL,
  FOREIGN KEY (custom_field_id) REFERENCES custom_field_definitions(custom_field_id) ON DELETE CASCADE,
  UNIQUE (custom_field_id, sort_order),
  UNIQUE (custom_field_id, name)
);

-- Which custom fields are enabled/used in a project (project-specific configuration)
CREATE TABLE project_custom_fields (
  project_id      TEXT NOT NULL,
  custom_field_id TEXT NOT NULL,
  is_required     INTEGER NOT NULL DEFAULT 0,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (project_id, custom_field_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
  FOREIGN KEY (custom_field_id) REFERENCES custom_field_definitions(custom_field_id) ON DELETE CASCADE
);

-- Values on tasks (one row per task-field pair).
-- This mirrors “custom field values recorded on a task/project” concept in Asana’s data model [web:11].
CREATE TABLE task_custom_field_values (
  task_id         TEXT NOT NULL,
  custom_field_id TEXT NOT NULL,

  -- store one of these depending on field_type:
  text_value      TEXT,
  number_value    REAL,
  date_value      TEXT,                          -- YYYY-MM-DD
  enum_option_id  TEXT,                          -- for enum/multi_enum (multi handled via multiple rows)
  people_user_id  TEXT,                          -- for people-type custom fields

  updated_at      TEXT NOT NULL,
  PRIMARY KEY (task_id, custom_field_id, enum_option_id, people_user_id),
  FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
  FOREIGN KEY (custom_field_id) REFERENCES custom_field_definitions(custom_field_id) ON DELETE CASCADE,
  FOREIGN KEY (enum_option_id) REFERENCES custom_field_enum_options(option_id) ON DELETE CASCADE,
  FOREIGN KEY (people_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_tcfv_task ON task_custom_field_values(task_id);
CREATE INDEX idx_tcfv_field ON task_custom_field_values(custom_field_id);

-- ========== Tags ==========

CREATE TABLE tags (
  tag_id       TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name         TEXT NOT NULL,
  color        TEXT,
  created_at   TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
  UNIQUE (workspace_id, name)
);

CREATE TABLE task_tags (
  task_id TEXT NOT NULL,
  tag_id  TEXT NOT NULL,
  PRIMARY KEY (task_id, tag_id),
  FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
