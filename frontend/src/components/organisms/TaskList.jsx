import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  InputAdornment,
  TextField,
  Button,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { Search as SearchIcon } from '@mui/icons-material';
import { fetchMyTasks, clearError } from '../../store/taskSlice';
import TaskItem from '../molecules/TaskItem';
import CreateTaskModal from '../molecules/CreateTaskModal';

const TaskList = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error } = useSelector((state) => state.tasks);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchMyTasks());
  }, [dispatch]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value.toLowerCase());
  };

  const filterTasks = (tasks) => {
    return tasks.filter(task => {
      // Filter by status
      if (activeTab !== 'all' && task.status !== activeTab) {
        return false;
      }
      
      // Filter by search query
      if (searchQuery) {
        return (
          task.title.toLowerCase().includes(searchQuery) ||
          task.description?.toLowerCase().includes(searchQuery) ||
          task.assignee?.full_name.toLowerCase().includes(searchQuery)
        );
      }
      
      return true;
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert
          severity="error"
          onClose={() => dispatch(clearError())}
          sx={{ mb: 2 }}
        >
          {error.detail || 'An error occurred while fetching tasks'}
        </Alert>
      )}

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          sx={{ flex: 1 }}
          fullWidth
          variant="outlined"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateModalOpen(true)}
        >
          Create Task
        </Button>

        <CreateTaskModal
          open={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />
      </Box>

      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 3 }}
      >
        <Tab label="All Tasks" value="all" />
        <Tab label="New" value="new" />
        <Tab label="In Progress" value="in_progress" />
        <Tab label="Pending Review" value="pending_review" />
        <Tab label="Completed" value="completed" />
      </Tabs>

      {tasks.length === 0 ? (
        <Typography
          variant="body1"
          color="text.secondary"
          align="center"
          sx={{ py: 4 }}
        >
          No tasks found
        </Typography>
      ) : (
        <Box>
          {filterTasks(tasks).map((task) => (
            <TaskItem key={task.id} task={task} />
          ))}
        </Box>
      )}
    </Box>
  );
};

export default TaskList;
