# Create Stories Batch - Workflow Instructions

````xml
<critical>The workflow execution engine is governed by: {project_root}/bmad/core/tasks/workflow.xml</critical>
<critical>You MUST have already loaded and processed: {installed_path}/workflow.yaml</critical>
<critical>This workflow creates multiple user stories in batch by invoking the create-story workflow repeatedly</critical>
<critical>Generate all documents in {document_output_language}</critical>
<critical>DOCUMENT OUTPUT: Multiple story documents created sequentially</critical>

<workflow>

  <step n="1" goal="Load config and initialize">
    <action>Resolve variables from config_source: story_dir (dev_story_location), output_folder, user_name, communication_language. If story_dir missing and {{non_interactive}} == false → ASK user to provide a stories directory and update variable. If {{non_interactive}} == true and missing, HALT with a clear message.</action>
    <action>Create {{story_dir}} if it does not exist</action>
    <action>Resolve sprint_status_file path: {{output_folder}}/sprint-status.yaml</action>
    <action>Load create-story workflow path: {project-root}/bmad/bmm/workflows/4-implementation/create-story/workflow.yaml</action>
  </step>

  <step n="2" goal="Discover backlog stories">
    <action>Load the FULL file: {{sprint_status_file}}</action>
    <action>Read ALL lines from beginning to end - do not skip any content</action>
    <action>Parse the development_status section completely</action>
    
    <action>Find ALL stories with status "backlog":
      - Key matches pattern: number-number-name (e.g., "1-2-user-auth")
      - NOT an epic key (epic-X) or retrospective (epic-X-retrospective)
      - Status value equals "backlog"
      - Preserve order from file (top to bottom)
    </action>
    
    <action>Store all backlog story keys in {{backlog_stories}} array, preserving file order</action>
    <action>Count backlog stories and store in {{backlog_count}}</action>
    
    <check if="no backlog stories found">
      <output>📋 No backlog stories found in sprint-status.yaml

All stories are either already drafted or completed.

**Options:**
1. Run sprint-planning to refresh story tracking
2. Load PM agent and run correct-course to add more stories
3. Check if current sprint is complete
      </output>
      <action>HALT</action>
    </check>
    
    <output>📊 **Backlog Stories Found: {{backlog_count}}**

Stories to process (in order):
{{backlog_stories}} (list each story key)

      </output>
  </step>

  <step n="3" goal="Determine batch size">
    <action>If {{max_stories}} is empty or not specified:
      - If {{non_interactive}} == true → Process ALL backlog stories ({{backlog_count}})
      - If {{non_interactive}} == false → ASK user: "How many stories to create? (Enter number or 'all' for {{backlog_count}})"
    </action>
    
    <action>If {{max_stories}} is provided:
      - Parse as integer (n)
      - Set batch_size = min(n, {{backlog_count}})
      - If {{non_interactive}} == false → Confirm: "Creating {{batch_size}} stories. Continue? (y/n)"
    </action>
    
    <action>Store final batch_size in {{batch_size}}</action>
    <action>Select first {{batch_size}} stories from {{backlog_stories}} array, store in {{stories_to_create}}</action>
    
    <output>✅ **Batch Configuration**

- Total backlog: {{backlog_count}} stories
- Batch size: {{batch_size}} stories
- Stories to create: {{stories_to_create}} (list)

Ready to begin batch creation...
      </output>
  </step>

  <step n="4" goal="Create stories in batch">
    <action>Initialize counters: {{created_count}} = 0, {{skipped_count}} = 0, {{failed_count}} = 0</action>
    <action>Initialize result arrays: {{created_stories}} = [], {{skipped_stories}} = [], {{failed_stories}} = []</action>
    
    <action>For iteration from 1 to {{batch_size}}:
      
      1. Display progress: "Creating story {{iteration}}/{{batch_size}}..."
      
      2. Load sprint-status.yaml to check current backlog state:
         - Read the FULL file again
         - Find first story with status "backlog" (by file order)
         - If no backlog story found → Break loop, all stories processed
         - Extract current_story_key from found story
      
      3. Check if this story was in our original {{stories_to_create}} list:
         - If current_story_key not in {{stories_to_create}} → This means a story was created outside our batch, skip iteration
         - If current_story_key in {{stories_to_create}} but already processed → Skip iteration
      
      4. Check if story file already exists:
         - Path: {{story_dir}}/{{current_story_key}}.md
         - If exists and {{non_interactive}} == false → ASK: "Story {{current_story_key}} already exists. Skip [s], Overwrite [o], or Cancel [c]?"
         - If exists and {{non_interactive}} == true → Mark as skipped, add to {{skipped_stories}}, increment {{skipped_count}}, continue to next iteration
      
      5. Invoke create-story workflow (which will find and create the first backlog story):
         <invoke-workflow path="{project-root}/bmad/bmm/workflows/4-implementation/create-story/workflow.yaml">
         </invoke-workflow>
      
      6. Check result after workflow completes:
         - Reload sprint-status.yaml to check if story status changed from "backlog" to "drafted"
         - If status changed → Increment {{created_count}}, add {{current_story_key}} to {{created_stories}}
         - If status still "backlog" or story creation failed → Increment {{failed_count}}, add {{current_story_key}} to {{failed_stories}}
      
      7. Display intermediate result: "✓ Story {{current_story_key}}: {{result}} ({{created_count}} created so far)"
      
      8. If {{non_interactive}} == false → ASK: "Continue with next story? (y/n)"
      
      9. Mark {{current_story_key}} as processed to avoid duplicates
    </action>
  </step>

  <step n="5" goal="Generate batch summary">
    <action>Calculate summary statistics:
      - Total processed: {{batch_size}}
      - Created: {{created_count}}
      - Skipped: {{skipped_count}}
      - Failed: {{failed_count}}
    </action>
    
    <output>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**✅ Batch Story Creation Complete, {user_name}!**

**Summary:**
- Total processed: {{batch_size}} stories
- ✅ Created: {{created_count}} stories
- ⏭️ Skipped: {{skipped_count}} stories
- ❌ Failed: {{failed_count}} stories

**Created Stories:**
{{created_stories}} (list each with file path)

**Skipped Stories:**
{{skipped_stories}} (list each with reason)

**Failed Stories:**
{{failed_stories}} (list each with error if available)

**Next Steps:**
1. Review created story files in {{story_dir}}
2. Run `story-context` for each created story to generate technical context XML
3. Or use batch context generation if available

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      </output>
  </step>

</workflow>
````

