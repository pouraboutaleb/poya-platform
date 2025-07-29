import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  IconButton,
} from '@mui/material';
import { deleteTask } from '../../store/taskSlice';
import EditTaskModal from './EditTaskModal';
import ChangeRequestApprovalView from './ChangeRequestApprovalView';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Create as CreateIcon,
  RateReview as ReviewIcon,
} from '@mui/icons-material';

const priorityColors = {
  1: 'info',
  2: 'success',
  3: 'warning',
  4: 'error',
};

const priorityLabels = {
  1: 'Low',
  2: 'Medium',
  3: 'High',
  4: 'Urgent',
};

const statusColors = {
  new: 'info',
  in_progress: 'warning',
  pending_review: 'secondary',
  needs_revision: 'error',
  completed: 'success',
  canceled: 'default',
};

const formatDate = (dateString) => {
  if (!dateString) return 'Not set';
  return new Date(dateString).toLocaleString();
};

const TaskDetailView = ({ task, open, onClose }) => {
  const dispatch = useDispatch();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);

  const handleEdit = () => {
    setIsEditModalOpen(true);
  };

  const handleDelete = async () => {
    try {
      await dispatch(deleteTask(task.id)).unwrap();
      onClose();
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };
  // Check if this is a change request approval task
  const isChangeRequestTask = task?.type === 'change_request_approval';

  if (!task) return null;

  return (
    <>
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" component="div">
            Task Details
          </Typography>
          <Box>
              {isChangeRequestTask ? (
                <IconButton
                  color="primary"
                  onClick={() => setIsApprovalModalOpen(true)}
                  title="Review Change Request"
                >
                  <ReviewIcon />
                </IconButton>
              ) : (
                <IconButton 
                  color="primary" 
                  onClick={handleEdit}
                  title="Edit Task"
                >
                  <EditIcon />
                </IconButton>
              )}
              <IconButton 
                color="error" 
                onClick={() => setIsDeleteDialogOpen(true)}
                title="Delete Task"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            {task.title}
          </Typography>
          
          <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 2 }}>
            <Chip
              label={priorityLabels[task.priority]}
              color={priorityColors[task.priority]}
            />
            <Chip
              label={task.status.replace('_', ' ')}
              color={statusColors[task.status]}
            />
            {isChangeRequestTask && (
              <Chip
                label="Change Request Review"
                color="primary"
                icon={<ReviewIcon />}
              />
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Description
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {task.description || 'No description provided'}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Task Details
          </Typography>
          
          <Box display="flex" flexDirection="column" gap={1}>
            <Box display="flex" alignItems="center" gap={1}>
              <PersonIcon color="action" />
              <Typography variant="body1">
                <strong>Assignee:</strong> {task.assignee?.full_name || 'Unassigned'}
              </Typography>
            </Box>

            <Box display="flex" alignItems="center" gap={1}>
              <CreateIcon color="action" />
              <Typography variant="body1">
                <strong>Creator:</strong> {task.creator?.full_name}
              </Typography>
            </Box>

            <Box display="flex" alignItems="center" gap={1}>
              <ScheduleIcon color="action" />
              <Typography variant="body1">
                <strong>Due Date:</strong> {formatDate(task.due_date)}
              </Typography>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Timeline
          </Typography>
          
          <Box display="flex" flexDirection="column" gap={1}>
            <Typography variant="body2" color="text.secondary">
              <strong>Created:</strong> {formatDate(task.created_at)}
            </Typography>
            {task.updated_at && (
              <Typography variant="body2" color="text.secondary">
                <strong>Last Updated:</strong> {formatDate(task.updated_at)}
              </Typography>
            )}
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
          {isChangeRequestTask ? (
            <Button
              onClick={() => setIsApprovalModalOpen(true)}
              startIcon={<ReviewIcon />}
              color="primary"
              variant="contained"
            >
              Review Change Request
            </Button>
          ) : (
            <>
              <Button onClick={handleEdit} startIcon={<EditIcon />} color="primary">
                Edit
              </Button>
              <Button 
                onClick={() => setIsDeleteDialogOpen(true)} 
                startIcon={<DeleteIcon />} 
                color="error"
              >
                Delete
              </Button>
            </>
          )}
      </DialogActions>

      {/* Edit Modal */}
      {isEditModalOpen && (
        <EditTaskModal
          task={task}
          open={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
        />
      )}

      {/* Change Request Approval Modal */}
      {isChangeRequestTask && (
        <ChangeRequestApprovalView
          open={isApprovalModalOpen}
          onClose={() => setIsApprovalModalOpen(false)}
          task={task}
        />
      )}

      {/* Edit Modal */}
      {isEditModalOpen && (
        <EditTaskModal
          task={task}
          open={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Delete Task</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{task.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default TaskDetailView;
