import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  Divider,
  IconButton,
  Grid,
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { CloudUpload as UploadIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Editor } from '@tinymce/tinymce-react';
import UserSelect from '../atoms/UserSelect';
import { createMeetingMinutes, updateMeetingMinutes } from '../../store/meetingSlice';

const MeetingMinutesForm = ({ open, onClose, meeting, existingMinutes = null }) => {
  const dispatch = useDispatch();
  const [minutes, setMinutes] = useState(existingMinutes?.text_body || '');
  const [attachments, setAttachments] = useState(existingMinutes?.attachments || []);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    assignee_id: null,
    due_date: null,
  });
  const [tasks, setTasks] = useState([]);

  const handleEditorChange = (content) => {
    setMinutes(content);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`/api/v1/meetings/${meeting.id}/minutes/attachments`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setAttachments([...attachments, data.file_url]);
    } catch (error) {
      console.error('Failed to upload file:', error);
    }
  };

  const handleAddTask = () => {
    if (newTask.title && newTask.assignee_id) {
      setTasks([...tasks, { ...newTask }]);
      setNewTask({
        title: '',
        description: '',
        assignee_id: null,
        due_date: null,
      });
    }
  };

  const handleRemoveTask = (index) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    const minutesData = {
      text_body: minutes,
      attachments,
      tasks,
    };

    try {
      if (existingMinutes) {
        await dispatch(updateMeetingMinutes({ meetingId: meeting.id, minutes: minutesData })).unwrap();
      } else {
        await dispatch(createMeetingMinutes({ meetingId: meeting.id, minutes: minutesData })).unwrap();
      }
      onClose();
    } catch (error) {
      console.error('Failed to save minutes:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        {existingMinutes ? 'Edit Meeting Minutes' : 'Add Meeting Minutes'}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Minutes
          </Typography>
          <Editor
            value={minutes}
            onEditorChange={handleEditorChange}
            init={{
              height: 400,
              menubar: false,
              plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount'
              ],
              toolbar: 'undo redo | formatselect | ' +
                'bold italic backcolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
            }}
          />
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Attachments
          </Typography>
          <input
            accept="*/*"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            onChange={handleFileUpload}
          />
          <label htmlFor="file-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<UploadIcon />}
            >
              Upload File
            </Button>
          </label>
          
          {attachments.map((url, index) => (
            <Box key={index} display="flex" alignItems="center" mt={1}>
              <Typography noWrap sx={{ flex: 1 }}>
                {url.split('/').pop()}
              </Typography>
              <IconButton 
                size="small"
                onClick={() => setAttachments(attachments.filter((_, i) => i !== index))}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          ))}
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Create Tasks from Minutes
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Task Title"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <UserSelect
                value={newTask.assignee_id}
                onChange={(value) => setNewTask({ ...newTask, assignee_id: value })}
                label="Assignee"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateTimePicker
                  label="Due Date"
                  value={newTask.due_date}
                  onChange={(value) => setNewTask({ ...newTask, due_date: value })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Task Description"
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </Grid>
          </Grid>

          <Button
            variant="contained"
            onClick={handleAddTask}
            disabled={!newTask.title || !newTask.assignee_id}
          >
            Add Task
          </Button>

          {tasks.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Tasks to be created:
              </Typography>
              {tasks.map((task, index) => (
                <Box key={index} sx={{ mt: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">{task.title}</Typography>
                    <IconButton size="small" onClick={() => handleRemoveTask(index)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Save Minutes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MeetingMinutesForm;
