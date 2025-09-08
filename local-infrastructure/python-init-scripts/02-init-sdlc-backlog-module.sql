-- SDLC Backlog Module Database Schema Initialization
-- This script initializes the schema for the sdlc_backlog_module database
-- Supports hierarchical backlog items: Epics -> Features -> User Stories -> Acceptance Criteria

-- Connect to the sdlc_backlog_module database
\c sdlc_backlog_module;

-- AI Context Management Schema
CREATE TABLE ai_context (
    id VARCHAR(50) PRIMARY KEY,
    context TEXT NULL, -- Context through text
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- AI Context Embedding Schema (created first to support business workflow)
CREATE TABLE ai_file_embeddings (
    id VARCHAR(50) PRIMARY KEY,
    topic_metadata TEXT NULL, -- Context metadata to imprpve the search and semantic, keywords similarities with the user request
    embedding_vector VECTOR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- AI Context File Schema (references embeddings - created after successful embedding processing)
CREATE TABLE ai_context_file (
    id VARCHAR(50) PRIMARY KEY,
    file_name VARCHAR(50) NOT NULL,
    file_size BIGINT NULL,
    file_type VARCHAR(10) NULL,
    hash_file VARCHAR(150) NULL, -- Hash file with the purpose of identify documents previously embedded 
    ai_context_id VARCHAR(50) NOT NULL,
    ai_file_embeddings_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ai_context_file_ai_context FOREIGN KEY (ai_context_id) REFERENCES ai_context(id) ON DELETE CASCADE,
    CONSTRAINT fk_ai_context_file_ai_file_embeddings_id FOREIGN KEY (ai_file_embeddings_id) REFERENCES ai_file_embeddings(id) ON DELETE CASCADE
);

-- Project Management Schema
CREATE TABLE project (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL, -- Simple Project description 
    status VARCHAR(15) NOT NULL DEFAULT 'ACTIVE',
    ai_context_id VARCHAR(50) NOT NULL, -- Every project could have an AI context that could be text, files or both
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_project_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED', 'COMPLETED', 'ON_HOLD'))
);

-- Backlog Item Type Definitions
CREATE TABLE backlog_item_template (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- System Prompts Main Table
CREATE TABLE backlog_item_system_prompt (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Backlog Item Type Definitions
CREATE TABLE backlog_item_type (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL, -- 1=Epic, 2=Feature, 3=User Story, 4=Acceptance Criteria
    template_id VARCHAR(50) NULL,
    system_prompt_id VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_backlog_item_type_template FOREIGN KEY (template_id) REFERENCES backlog_item_template(id),
    CONSTRAINT fk_backlog_item_system_prompt FOREIGN KEY (system_prompt_id) REFERENCES backlog_item_system_prompt(id),
    CONSTRAINT chk_backlog_item_type_level CHECK (level BETWEEN 1 AND 4)
);

-- Hierarchical Backlog Items Schema
CREATE TABLE backlog_item (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    status VARCHAR(15) NOT NULL DEFAULT 'TODO', -- TODO, IN_PROGRESS, DONE, BLOCKED
    priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
    story_points INTEGER NULL,
    synchronized_alm BOOLEAN NOT NULL DEFAULT FALSE,
    type_id VARCHAR(50) NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    ai_context_id VARCHAR(50) NOT NULL, -- Every backlog item MUST have an AI context
    parent_item_id VARCHAR(50) NULL, -- Self-referencing for hierarchy
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_backlog_item_type FOREIGN KEY (type_id) REFERENCES backlog_item_type(id),
    CONSTRAINT fk_backlog_item_project FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
    CONSTRAINT fk_backlog_item_parent FOREIGN KEY (parent_item_id) REFERENCES backlog_item(id) ON DELETE CASCADE,
    CONSTRAINT chk_backlog_item_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED')),
    CONSTRAINT chk_backlog_item_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- Add foreign key constraints for required ai_context_id references
ALTER TABLE project ADD CONSTRAINT fk_project_ai_context FOREIGN KEY (ai_context_id) REFERENCES ai_context(id);
ALTER TABLE backlog_item ADD CONSTRAINT fk_backlog_item_ai_context FOREIGN KEY (ai_context_id) REFERENCES ai_context(id);

-- Insert default backlog item types with hierarchy levels
INSERT INTO backlog_item_type (id, name, level) VALUES
('epic', 'Epic', 1),
('feature', 'Feature', 2),
('user_story', 'User Story', 3),
('acceptance_criteria', 'Acceptance Criteria', 4);

-- Indexes for performance
CREATE INDEX idx_backlog_item_project_id ON backlog_item(project_id);
CREATE INDEX idx_backlog_item_parent_id ON backlog_item(parent_item_id);
CREATE INDEX idx_backlog_item_type_id ON backlog_item(type_id);
CREATE INDEX idx_backlog_item_status ON backlog_item(status);
CREATE INDEX idx_backlog_item_priority ON backlog_item(priority);
CREATE INDEX idx_backlog_item_ai_context_id ON backlog_item(ai_context_id);
CREATE INDEX idx_project_ai_context_id ON project(ai_context_id);
CREATE INDEX idx_ai_context_file_context_id ON ai_context_file(ai_context_id);
CREATE INDEX idx_ai_file_embeddings_id ON ai_file_embeddings(id);
CREATE INDEX idx_ai_context_file_embeddings_id ON ai_context_file(ai_file_embeddings_id);
CREATE INDEX idx_backlog_item_sort_order ON backlog_item(project_id, parent_item_id, sort_order);

-- Function to check for circular references in hierarchy
CREATE OR REPLACE FUNCTION check_circular_reference(item_id VARCHAR(50), parent_id VARCHAR(50))
RETURNS BOOLEAN AS $$
DECLARE
    current_parent VARCHAR(50);
    max_depth INTEGER := 10; -- Prevent infinite loops
    depth INTEGER := 0;
BEGIN
    current_parent := parent_id;
    
    WHILE current_parent IS NOT NULL AND depth < max_depth LOOP
        -- If we find the original item_id in the parent chain, it's circular
        IF current_parent = item_id THEN
            RETURN TRUE; -- Circular reference found
        END IF;
        
        -- Get the next parent
        SELECT parent_item_id INTO current_parent 
        FROM backlog_item 
        WHERE id = current_parent;
        
        depth := depth + 1;
    END LOOP;
    
    RETURN FALSE; -- No circular reference
END;
$$ LANGUAGE plpgsql;

-- Function to validate hierarchy constraints
CREATE OR REPLACE FUNCTION validate_backlog_item_hierarchy()
RETURNS TRIGGER AS $$
DECLARE
    parent_type_level INTEGER;
    current_type_level INTEGER;
BEGIN
    -- Get the level of the current item type
    SELECT level INTO current_type_level
    FROM backlog_item_type
    WHERE id = NEW.type_id;
    
    -- If there's a parent, validate the hierarchy
    IF NEW.parent_item_id IS NOT NULL THEN
        -- Get the parent's type level
        SELECT bt.level INTO parent_type_level
        FROM backlog_item bi
        JOIN backlog_item_type bt ON bi.type_id = bt.id
        WHERE bi.id = NEW.parent_item_id;
        
        -- Validate that parent level is exactly one level above current level
        IF parent_type_level IS NULL OR parent_type_level != (current_type_level - 1) THEN
            RAISE EXCEPTION 'Invalid hierarchy: % (level %) cannot be child of item with level %', 
                NEW.type_id, current_type_level, parent_type_level;
        END IF;
        
        -- Ensure parent and child are in the same project
        IF NOT EXISTS (
            SELECT 1 FROM backlog_item 
            WHERE id = NEW.parent_item_id AND project_id = NEW.project_id
        ) THEN
            RAISE EXCEPTION 'Parent item must be in the same project';
        END IF;
        
        -- Check for circular references
        IF check_circular_reference(NEW.id, NEW.parent_item_id) THEN
            RAISE EXCEPTION 'Circular reference detected: item % cannot have parent % (would create a loop)', 
                NEW.id, NEW.parent_item_id;
        END IF;
    ELSE
        -- If no parent, must be an Epic (level 1)
        IF current_type_level != 1 THEN
            RAISE EXCEPTION 'Only Epics (level 1) can exist without a parent';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for hierarchy validation
CREATE TRIGGER tr_validate_backlog_item_hierarchy
    BEFORE INSERT OR UPDATE ON backlog_item
    FOR EACH ROW
    EXECUTE FUNCTION validate_backlog_item_hierarchy();

-- Function to automatically update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER tr_update_project_timestamp
    BEFORE UPDATE ON project
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_update_backlog_item_timestamp
    BEFORE UPDATE ON backlog_item
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_update_ai_context_timestamp
    BEFORE UPDATE ON ai_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_update_backlog_item_system_prompt_timestamp
    BEFORE UPDATE ON backlog_item_system_prompt
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_update_backlog_item_template_timestamp
    BEFORE UPDATE ON backlog_item_template
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_update_backlog_item_type_timestamp
    BEFORE UPDATE ON backlog_item_type
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Helpful Views for Hierarchical Data Access

-- View to see complete hierarchy path for each backlog item
-- Note: Explicit casting to avoid PostgreSQL recursive CTE type issues
CREATE VIEW v_backlog_item_hierarchy AS
WITH RECURSIVE item_hierarchy AS (
    -- Base case: Root items (Epics)
    SELECT 
        bi.id,
        bi.title,
        bi.description,
        bi.status,
        bi.priority,
        bi.story_points,
        bi.project_id,
        bi.type_id,
        bit.name as type_name,
        bit.level as type_level,
        bi.parent_item_id,
        bi.sort_order,
        1 as depth,
        bi.id::TEXT as path_string,
        bi.title::TEXT as full_path
    FROM backlog_item bi
    JOIN backlog_item_type bit ON bi.type_id = bit.id
    WHERE bi.parent_item_id IS NULL
    
    UNION ALL
    
    -- Recursive case: Child items
    SELECT 
        bi.id,
        bi.title,
        bi.description,
        bi.status,
        bi.priority,
        bi.story_points,
        bi.project_id,
        bi.type_id,
        bit.name as type_name,
        bit.level as type_level,
        bi.parent_item_id,
        bi.sort_order,
        ih.depth + 1,
        ih.path_string || '/' || bi.id::TEXT as path_string,
        ih.full_path || ' -> ' || bi.title::TEXT as full_path
    FROM backlog_item bi
    JOIN backlog_item_type bit ON bi.type_id = bit.id
    JOIN item_hierarchy ih ON bi.parent_item_id = ih.id
)
SELECT 
    ih.*,
    p.name as project_name,
    p.description as project_description
FROM item_hierarchy ih
JOIN project p ON ih.project_id = p.id
ORDER BY ih.project_id, ih.path_string;

-- View for project summary with counts by item type
CREATE VIEW v_project_backlog_summary AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.description as project_description,
    p.status as project_status,
    COUNT(CASE WHEN bit.level = 1 THEN 1 END) as epics_count,
    COUNT(CASE WHEN bit.level = 2 THEN 1 END) as features_count,
    COUNT(CASE WHEN bit.level = 3 THEN 1 END) as user_stories_count,
    COUNT(CASE WHEN bit.level = 4 THEN 1 END) as acceptance_criteria_count,
    COUNT(bi.id) as total_items,
    COUNT(CASE WHEN bi.status = 'DONE' THEN 1 END) as completed_items,
    ROUND(
        CASE 
            WHEN COUNT(bi.id) > 0 
            THEN (COUNT(CASE WHEN bi.status = 'DONE' THEN 1 END) * 100.0 / COUNT(bi.id))
            ELSE 0 
        END, 2
    ) as completion_percentage
FROM project p
LEFT JOIN backlog_item bi ON p.id = bi.project_id
LEFT JOIN backlog_item_type bit ON bi.type_id = bit.id
GROUP BY p.id, p.name, p.description, p.status
ORDER BY p.name;

-- Example usage queries (commented out, for reference)
/*
-- Example workflow: Create project with AI context
-- Step 1: Create AI context first
INSERT INTO ai_context (id, context) VALUES 
('ctx_proj_001', 'E-commerce platform development context with microservices, user authentication, and payment processing');

-- Step 2: Create project referencing the AI context
INSERT INTO project (id, name, description, ai_context_id) VALUES 
('proj_001', 'E-Commerce Platform', 'Modern e-commerce platform with microservices architecture', 'ctx_proj_001');

-- Example workflow: Create hierarchical backlog items with AI contexts
-- Step 3: Create Epic with its AI context
INSERT INTO ai_context (id, context) VALUES 
('ctx_epic_001', 'User management system context: OAuth2, JWT tokens, role-based access control, user profiles');

INSERT INTO backlog_item (id, title, description, type_id, project_id, ai_context_id, priority) VALUES 
('epic_001', 'User Management System', 'Complete user registration, authentication, and profile management', 'epic', 'proj_001', 'ctx_epic_001', 'HIGH');

-- Step 4: Create Feature under Epic with its AI context
INSERT INTO ai_context (id, context) VALUES 
('ctx_feat_001', 'User registration feature: form validation, email verification, account creation workflow');

INSERT INTO backlog_item (id, title, description, type_id, project_id, ai_context_id, parent_item_id, priority) VALUES 
('feat_001', 'User Registration', 'Allow new users to create accounts', 'feature', 'proj_001', 'ctx_feat_001', 'epic_001', 'HIGH');

-- Step 5: Create User Story under Feature with its AI context
INSERT INTO ai_context (id, context) VALUES 
('ctx_story_001', 'Email registration: validation patterns, duplicate checks, confirmation emails, GDPR compliance');

INSERT INTO backlog_item (id, title, description, type_id, project_id, ai_context_id, parent_item_id, story_points) VALUES 
('story_001', 'User can register with email', 'As a new user, I want to register with my email address so that I can create an account', 'user_story', 'proj_001', 'ctx_story_001', 'feat_001', 3);

-- Step 6: Create Acceptance Criteria under User Story with its AI context
INSERT INTO ai_context (id, context) VALUES 
('ctx_ac_001', 'Email validation requirements: format validation, domain checking, forbidden email patterns');

INSERT INTO backlog_item (id, title, description, type_id, project_id, ai_context_id, parent_item_id) VALUES 
('ac_001', 'Email validation required', 'System must validate email format before allowing registration', 'acceptance_criteria', 'proj_001', 'ctx_ac_001', 'story_001');

-- Example: Create AI context with file-based information (Business Workflow)
-- Step 1: Create AI context first
INSERT INTO ai_context (id, context) VALUES 
('ctx_with_files', 'Project specification and requirements');

-- Step 2: Process file and create embeddings first (this must succeed before file record)
INSERT INTO ai_file_embeddings (id, topic_metadata, embedding_vector, hash_file) VALUES 
('embed_001', 'User registration specifications', '[0.1, 0.2, 0.3]'::vector, 'hash123456');

-- Step 3: Only after successful embedding processing, create the file record
INSERT INTO ai_context_file (id, file_name, file_size, file_type, ai_context_id, ai_file_embeddings_id) VALUES 
('file_001', 'user_registration_specs.pdf', 1024000, 'application/pdf', 'ctx_with_files', 'embed_001');

-- Example: Business workflow with multiple files for same context
-- If embedding processing fails, ai_context_file is never created, keeping data integrity
INSERT INTO ai_file_embeddings (id, topic_metadata, embedding_vector, hash_file) VALUES 
('embed_002', 'API specifications', '[0.4, 0.5, 0.6]'::vector, 'hash789012');

INSERT INTO ai_context_file (id, file_name, file_size, file_type, ai_context_id, ai_file_embeddings_id) VALUES 
('file_002', 'api_specifications.json', 2048000, 'application/json', 'ctx_with_files', 'embed_002');

-- Query examples:
-- Get complete hierarchy for a project
SELECT * FROM v_backlog_item_hierarchy WHERE project_id = 'proj_001';

-- Get project summary
SELECT * FROM v_project_backlog_summary WHERE project_id = 'proj_001';

-- Get all children of a specific item
SELECT * FROM backlog_item WHERE parent_item_id = 'epic_001';

-- Get AI context for a project (directly through project table)
SELECT p.id as project_id, p.name, ac.* 
FROM project p 
JOIN ai_context ac ON p.ai_context_id = ac.id 
WHERE p.id = 'proj_001';

-- Get AI context for a specific backlog item (directly through backlog_item table)
SELECT bi.id as backlog_item_id, bi.title, ac.* 
FROM backlog_item bi 
JOIN ai_context ac ON bi.ai_context_id = ac.id 
WHERE bi.id = 'story_001';

-- Get all AI contexts related to a project (project + all its backlog items)
SELECT ac.id, ac.context, 
       CASE 
           WHEN p.id IS NOT NULL THEN 'PROJECT'
           WHEN bi.id IS NOT NULL THEN 'BACKLOG_ITEM'
       END as context_type,
       COALESCE(p.name, bi.title) as associated_name
FROM ai_context ac
LEFT JOIN project p ON p.ai_context_id = ac.id AND p.id = 'proj_001'
LEFT JOIN backlog_item bi ON bi.ai_context_id = ac.id AND bi.project_id = 'proj_001'
WHERE p.id IS NOT NULL OR bi.id IS NOT NULL;

-- Get AI context with associated files
SELECT ac.id, ac.context, 
       acf.file_name, acf.file_size, acf.file_type,
       afe.topic_metadata, afe.hash_file
FROM ai_context ac
LEFT JOIN ai_context_file acf ON ac.id = acf.ai_context_id
LEFT JOIN ai_file_embeddings afe ON acf.ai_file_embeddings_id = afe.id
WHERE ac.id = 'ctx_with_files';

-- Get the complete path to root for a specific item
WITH RECURSIVE path_to_root AS (
    SELECT id, title, parent_item_id, 1 as level, title as path
    FROM backlog_item 
    WHERE id = 'ac_001'
    
    UNION ALL
    
    SELECT bi.id, bi.title, bi.parent_item_id, ptr.level + 1, bi.title || ' <- ' || ptr.path
    FROM backlog_item bi
    JOIN path_to_root ptr ON bi.id = ptr.parent_item_id
)
SELECT path FROM path_to_root WHERE parent_item_id IS NULL;
*/
